#!/usr/bin/env python3
"""Private, local Omnifeed storage foundation (Python standard library only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import secrets
import shutil
import sqlite3
import stat
import sys
import tempfile
import uuid
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
TOKEN_NAME = "device-token"


class OmniError(Exception):
    """Expected user-facing runtime error."""


def _private_dir(path: Path) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink() or not path.is_dir():
        raise OmniError(f"Not a safe directory: {path}")
    os.chmod(path, 0o700)


def _is_git_marker(path: Path) -> bool:
    marker = path / ".git"
    return marker.exists() or marker.is_symlink()


def _assert_outside_git(home: Path) -> None:
    """Reject a home inside a checkout and a home that contains a checkout.

    Ancestor checks are exact and cheap. Descendant checks walk only the
    requested existing home, without following symlinks. If the scan cannot
    prove the tree is clear within a conservative bound, fail closed.
    """
    for parent in (home, *home.parents):
        if _is_git_marker(parent):
            raise OmniError(f"Private runtime must be outside Git checkouts: {parent}")
    if home.exists():
        stack = [(home, 0)]
        visited = 0
        while stack:
            current, depth = stack.pop()
            visited += 1
            if visited > 100_000:
                raise OmniError("Cannot prove runtime location is outside Git checkouts (scan limit reached)")
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        if entry.name == ".git":
                            raise OmniError(f"Private runtime cannot contain a Git checkout: {current}")
                        if entry.is_dir(follow_symlinks=False):
                            if depth >= 64:
                                raise OmniError("Cannot prove runtime location is outside Git checkouts (depth limit reached)")
                            stack.append((Path(entry.path), depth + 1))
            except PermissionError as exc:
                raise OmniError(f"Cannot verify runtime location: {current}") from exc


def _validate_home(home: Path) -> Path:
    if not home.is_absolute():
        raise OmniError("Runtime home must be an absolute path")
    if home.is_symlink():
        raise OmniError("Runtime home cannot be a symlink")
    resolved = home.resolve(strict=False)
    _assert_outside_git(resolved)
    return resolved


def _managed_path(home: Path, path: Path) -> None:
    """Reject links and paths whose resolved ancestry escapes the private home."""
    home_real = home.resolve(strict=False)
    try:
        relative = path.relative_to(home)
    except ValueError as exc:
        raise OmniError("Managed path is outside runtime home") from exc
    current = home
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise OmniError(f"Managed runtime path cannot be a symlink: {current}")
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(home_real)
    except ValueError as exc:
        raise OmniError("Managed path resolves outside runtime home") from exc


def _regular_file(path: Path, label: str) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as exc:
        raise OmniError(f"{label} is missing: {path}") from exc
    if not stat.S_ISREG(mode):
        raise OmniError(f"{label} must be a regular file: {path}")


@contextmanager
def _connect(home: Path):
    db = home / "omnifeed.sqlite3"
    _managed_path(home, db)
    if db.exists():
        _regular_file(db, "Database")
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db) + suffix)
        _managed_path(home, sidecar)
        if sidecar.exists():
            _regular_file(sidecar, "Database sidecar")
    con = sqlite3.connect(db)
    try:
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        con.execute("PRAGMA journal_mode = WAL")
        os.chmod(db, 0o600)
        yield con
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def _preflight_schema(home: Path) -> None:
    db = home / "omnifeed.sqlite3"
    _managed_path(home, db)
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(db) + suffix)
        _managed_path(home, sidecar)
        if sidecar.exists():
            _regular_file(sidecar, "Database sidecar")
    if not db.exists():
        return
    _regular_file(db, "Database")
    # Read-only preflight prevents token, permission, and schema mutations when
    # the runtime cannot safely understand an existing database.
    uri = db.as_uri() + "?mode=ro"
    try:
        with closing(sqlite3.connect(uri, uri=True)) as con:
            tables = con.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchone()[0]
            exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='schema_meta'").fetchone()
            if exists:
                row = con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()
                try:
                    version = int(row[0]) if row else None
                except (TypeError, ValueError):
                    version = None
                if version != SCHEMA_VERSION:
                    raise OmniError(f"Unsupported or incomplete existing schema version: {row[0] if row else 'missing'}")
            elif tables:
                raise OmniError("Existing database has no Omnifeed schema; refusing to modify it")
    except sqlite3.DatabaseError as exc:
        raise OmniError("Existing database is unreadable; refusing to modify it") from exc


def _ensure_initialized(home: Path) -> None:
    home = _validate_home(home)
    _preflight_schema(home)
    _managed_path(home, home / "media")
    _managed_path(home, home / "secrets")
    _managed_path(home, home / "secrets" / TOKEN_NAME)
    db = home / "omnifeed.sqlite3"
    if not db.exists():
        raise OmniError("Runtime is not initialized; run `omni.py --home PATH init` first")
    _regular_file(db, "Database")
    token = home / "secrets" / TOKEN_NAME
    if not token.exists():
        raise OmniError("Device token is missing; run `omni.py --home PATH init` to repair the runtime")
    _regular_file(token, "Device token")
    if token.stat().st_size == 0:
        raise OmniError("Device token is empty; refusing to use an invalid secret")


def init(home: Path) -> None:
    home = _validate_home(home)
    _preflight_schema(home)
    _managed_path(home, home / "media")
    _managed_path(home, home / "secrets")
    _managed_path(home, home / "secrets" / TOKEN_NAME)
    token = home / "secrets" / TOKEN_NAME
    if token.exists():
        _regular_file(token, "Device token")
        if token.stat().st_size == 0:
            raise OmniError("Device token is empty; refusing to modify the runtime")
    _private_dir(home)
    _private_dir(home / "media")
    _private_dir(home / "secrets")
    if not token.exists():
        fd = os.open(token, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(secrets.token_urlsafe(32) + "\n")
        os.chmod(token, 0o600)
    else:
        os.chmod(token, 0o600)
    with _connect(home) as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS schema_meta (
                key TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS assets (
                id TEXT PRIMARY KEY, sha256 TEXT NOT NULL UNIQUE,
                media_path TEXT NOT NULL UNIQUE, original_name TEXT NOT NULL,
                size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
                imported_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
            );
            CREATE TABLE IF NOT EXISTS usage_events (
                id TEXT PRIMARY KEY, asset_id TEXT NOT NULL REFERENCES assets(id),
                event_type TEXT NOT NULL, progress_seconds REAL,
                duration_seconds REAL, device_id TEXT,
                occurred_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                metadata_json TEXT NOT NULL DEFAULT '{}',
                CHECK(progress_seconds IS NULL OR progress_seconds >= 0),
                CHECK(duration_seconds IS NULL OR duration_seconds >= 0)
            );
            CREATE INDEX IF NOT EXISTS usage_events_asset_time
                ON usage_events(asset_id, occurred_at);
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY, name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                last_seen_at TEXT
            );
        """)
        con.execute("INSERT OR IGNORE INTO schema_meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))
        version = con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0]
        if int(version) != SCHEMA_VERSION:
            raise OmniError(f"Unsupported schema version: {version}")
    os.chmod(home / "omnifeed.sqlite3", 0o600)
    # SQLite may create these companion files while open; restrict them too.
    for suffix in ("-wal", "-shm"):
        sidecar = Path(str(home / "omnifeed.sqlite3") + suffix)
        if sidecar.exists():
            os.chmod(sidecar, 0o600)


def status(home: Path) -> dict[str, Any]:
    _ensure_initialized(home)
    home = home.resolve(strict=False)
    _managed_path(home, home / "media")
    for path in (home / "media").rglob("*"):
        _managed_path(home, path)
    with _connect(home) as con:
        version = con.execute("SELECT value FROM schema_meta WHERE key='schema_version'").fetchone()[0]
        counts = {table: con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
                  for table in ("assets", "usage_events", "devices")}
    return {"initialized": True, "schema_version": int(version), **counts,
            "device_token_present": (home / "secrets" / TOKEN_NAME).is_file(),
            "media_bytes": sum(p.stat().st_size for p in (home / "media").rglob("*") if p.is_file())}


def _hash_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)
            total += len(chunk)
    return digest.hexdigest(), total


def import_media(home: Path, source: Path) -> dict[str, Any]:
    _ensure_initialized(home)
    home = home.resolve(strict=False)
    if source.is_symlink():
        raise OmniError("Symlink inputs are not accepted")
    try:
        resolved = source.resolve(strict=True)
        mode = resolved.stat().st_mode
    except (OSError, RuntimeError) as exc:
        raise OmniError(f"Cannot read input file: {source}") from exc
    if not stat.S_ISREG(mode):
        raise OmniError("Input must be a regular file")
    digest, size = _hash_file(resolved)
    rel = Path(digest[:2]) / digest
    dest = home / "media" / rel
    _managed_path(home, home / "media")
    _managed_path(home, dest.parent)
    _managed_path(home, dest)
    _private_dir(dest.parent)
    if dest.exists() and _hash_file(dest)[0] != digest:
        raise OmniError("Existing content-addressed file failed integrity check")
    if not dest.exists():
        fd, tmp_name = tempfile.mkstemp(prefix=".import-", dir=dest.parent)
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            shutil.copyfile(resolved, tmp)
            os.chmod(tmp, 0o600)
            if _hash_file(tmp)[0] != digest:
                raise OmniError("Input changed while it was being imported")
            os.replace(tmp, dest)
        finally:
            tmp.unlink(missing_ok=True)
    with _connect(home) as con:
        con.execute("PRAGMA foreign_keys = ON")
        row = con.execute("SELECT id, original_name, size_bytes FROM assets WHERE sha256=?", (digest,)).fetchone()
        if row:
            return {"id": row[0], "sha256": digest, "size_bytes": row[2], "already_imported": True}
        asset_id = str(uuid.uuid4())
        con.execute("INSERT INTO assets(id,sha256,media_path,original_name,size_bytes) VALUES(?,?,?,?,?)",
                    (asset_id, digest, str(rel), source.name, size))
        return {"id": asset_id, "sha256": digest, "size_bytes": size, "already_imported": False}


def record_event(home: Path, *, event_id: str, asset_id: str, event_type: str,
                 progress_seconds: float | None = None, duration_seconds: float | None = None,
                 device_id: str | None = None, metadata: dict[str, Any] | None = None) -> bool:
    _ensure_initialized(home)
    home = home.resolve(strict=False)
    try:
        event_id = str(uuid.UUID(event_id))
    except (ValueError, AttributeError) as exc:
        raise OmniError("event_id must be a UUID") from exc
    if not event_type.strip():
        raise OmniError("event_type cannot be blank")
    for label, value in (("progress_seconds", progress_seconds), ("duration_seconds", duration_seconds)):
        if value is not None and (not math.isfinite(value) or value < 0):
            raise OmniError(f"{label} must be finite and nonnegative")
    metadata = {} if metadata is None else metadata
    if not isinstance(metadata, dict):
        raise OmniError("metadata must be a JSON object")
    try:
        encoded = json.dumps(metadata, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise OmniError("metadata must contain JSON-safe values") from exc
    with _connect(home) as con:
        con.execute("PRAGMA foreign_keys = ON")
        try:
            existing = con.execute("SELECT asset_id,event_type,progress_seconds,duration_seconds,device_id,metadata_json FROM usage_events WHERE id=?", (event_id,)).fetchone()
            values = (asset_id, event_type.strip(), progress_seconds, duration_seconds, device_id, encoded)
            if existing:
                if tuple(existing) != values:
                    raise OmniError("event_id already exists with a different payload")
                return False
            cur = con.execute("INSERT INTO usage_events(id,asset_id,event_type,progress_seconds,duration_seconds,device_id,metadata_json) VALUES(?,?,?,?,?,?,?)",
                              (event_id, *values))
        except sqlite3.IntegrityError as exc:
            raise OmniError("Event references an unknown asset or violates the storage schema") from exc
        return cur.rowcount == 1


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local private Omnifeed storage runtime")
    parser.add_argument("--home", required=True, type=Path, help="absolute private data directory outside every Git checkout")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="create local schema, media store, and a private device token")
    sub.add_parser("status", help="show aggregate counts only")
    imp = sub.add_parser("import-media", help="copy a regular file into content-addressed private storage")
    imp.add_argument("path", type=Path)
    event = sub.add_parser("record-event", help="record an idempotent playback/use event")
    event.add_argument("--id", required=True, dest="event_id")
    event.add_argument("--asset", required=True, dest="asset_id")
    event.add_argument("--type", required=True, dest="event_type")
    event.add_argument("--progress", type=float, dest="progress_seconds")
    event.add_argument("--duration", type=float, dest="duration_seconds")
    event.add_argument("--device", dest="device_id")
    event.add_argument("--metadata", default="{}", help="JSON object")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        home = _validate_home(args.home)
        if args.command == "init":
            init(home)
            result = {"initialized": True, "home": str(home), "device_token_generated_or_preserved": True}
        else:
            _assert_outside_git(home)
            if args.command == "status":
                result = status(home)
            elif args.command == "import-media":
                result = import_media(home, args.path)
            else:
                try:
                    metadata = json.loads(args.metadata)
                except json.JSONDecodeError as exc:
                    raise OmniError("--metadata must be valid JSON") from exc
                inserted = record_event(home, event_id=args.event_id, asset_id=args.asset_id,
                                        event_type=args.event_type, progress_seconds=args.progress,
                                        duration_seconds=args.duration, device_id=args.device,
                                        metadata=metadata)
                result = {"recorded": inserted, "already_recorded": not inserted}
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OmniError, sqlite3.IntegrityError, sqlite3.Error, OSError) as exc:
        print(f"omni: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
