import os
import sqlite3
import stat
import tempfile
import unittest
import uuid
from contextlib import closing
from pathlib import Path

import omni


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "private" / "omni"
        omni.init(self.home)

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_is_idempotent_and_preserves_data_and_secret(self):
        token = (self.home / "secrets" / omni.TOKEN_NAME).read_text()
        src = self.root / "sample.bin"
        src.write_bytes(b"private sample")
        imported = omni.import_media(self.home, src)
        event_id = str(uuid.uuid4())
        self.assertTrue(omni.record_event(self.home, event_id=event_id, asset_id=imported["id"], event_type="played"))
        omni.init(self.home)
        self.assertEqual(token, (self.home / "secrets" / omni.TOKEN_NAME).read_text())
        self.assertEqual(1, omni.status(self.home)["assets"])
        self.assertEqual(1, omni.status(self.home)["usage_events"])

    def test_import_is_content_addressed_and_idempotent(self):
        src = self.root / "one.mp3"
        src.write_bytes(b"audio")
        first = omni.import_media(self.home, src)
        renamed = self.root / "renamed.mp3"
        renamed.write_bytes(b"audio")
        second = omni.import_media(self.home, renamed)
        self.assertFalse(first["already_imported"])
        self.assertTrue(second["already_imported"])
        self.assertEqual(first["id"], second["id"])
        self.assertTrue((self.home / "media" / first["sha256"][:2] / first["sha256"]).exists())

    def test_event_idempotency_and_validation(self):
        src = self.root / "media.dat"
        src.write_bytes(b"x")
        asset = omni.import_media(self.home, src)["id"]
        event = str(uuid.uuid4())
        self.assertTrue(omni.record_event(self.home, event_id=event, asset_id=asset, event_type="listen", progress_seconds=1.5))
        self.assertFalse(omni.record_event(self.home, event_id=event, asset_id=asset, event_type="listen", progress_seconds=1.5))
        with self.assertRaises(omni.OmniError):
            omni.record_event(self.home, event_id=event, asset_id=asset, event_type="listen", progress_seconds=2)
        with self.assertRaises(omni.OmniError):
            omni.record_event(self.home, event_id=str(uuid.uuid4()), asset_id=asset, event_type="listen", progress_seconds=float("nan"))
        with self.assertRaises(omni.OmniError):
            omni.record_event(self.home, event_id=str(uuid.uuid4()), asset_id="missing", event_type="listen")
        with self.assertRaises(omni.OmniError):
            omni.record_event(self.home, event_id=str(uuid.uuid4()), asset_id=asset, event_type="listen", metadata=[])

    def test_rejects_symlink_input_and_git_locations(self):
        src = self.root / "original"
        src.write_bytes(b"x")
        link = self.root / "link"
        link.symlink_to(src)
        with self.assertRaises(omni.OmniError):
            omni.import_media(self.home, link)
        repo = self.root / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        with self.assertRaises(omni.OmniError):
            omni.init(repo / "private")
        parent = self.root / "with-repo"
        (parent / "nested" / ".git").mkdir(parents=True)
        with self.assertRaises(omni.OmniError):
            omni.init(parent)

    def test_public_api_enforces_git_and_home_symlink_guards(self):
        repo = self.root / "direct-repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        with self.assertRaises(omni.OmniError):
            omni.init(repo / "runtime")
        outside = self.root / "actual-runtime"
        outside.mkdir()
        alias = self.root / "runtime-alias"
        alias.symlink_to(outside)
        with self.assertRaises(omni.OmniError):
            omni.init(alias)

    def test_rejects_symlink_ancestor_into_git(self):
        repo = self.root / "linked-repo"
        (repo / ".git").mkdir(parents=True)
        alias = self.root / "ancestor-alias"
        alias.symlink_to(repo, target_is_directory=True)
        with self.assertRaises(omni.OmniError):
            omni.init(alias / "runtime")
        self.assertFalse((repo / "runtime").exists())

    def test_rejects_symlink_managed_media_paths(self):
        src = self.root / "safe.bin"
        src.write_bytes(b"managed media")
        digest = omni._hash_file(src)[0]
        outside = self.root / "outside"
        outside.mkdir()
        (self.home / "media" / digest[:2]).symlink_to(outside, target_is_directory=True)
        with self.assertRaises(omni.OmniError):
            omni.import_media(self.home, src)
        self.assertEqual([], list(outside.iterdir()))

    def test_unsupported_schema_refuses_all_mutation(self):
        db = self.home / "omnifeed.sqlite3"
        token = self.home / "secrets" / omni.TOKEN_NAME
        token.unlink()
        os.chmod(self.home, 0o755)
        os.chmod(self.home / "media", 0o755)
        try:
            with __import__("sqlite3").connect(db) as con:
                con.execute("UPDATE schema_meta SET value='99' WHERE key='schema_version'")
            unsupported = db.read_bytes()
            with self.assertRaises(omni.OmniError):
                omni.init(self.home)
            self.assertFalse(token.exists())
            self.assertEqual(0o755, stat.S_IMODE(self.home.stat().st_mode))
            self.assertEqual(0o755, stat.S_IMODE((self.home / "media").stat().st_mode))
            self.assertEqual(unsupported, db.read_bytes())
            with sqlite3.connect(db) as con:
                con.execute("UPDATE schema_meta SET value='not-an-integer' WHERE key='schema_version'")
            malformed = db.read_bytes()
            with self.assertRaises(omni.OmniError):
                omni.init(self.home)
            self.assertEqual(malformed, db.read_bytes())
        finally:
            os.chmod(self.home, 0o700)
            os.chmod(self.home / "media", 0o700)

    def test_future_schema_blocks_media_import_and_event_writes(self):
        src = self.root / "known.bin"
        src.write_bytes(b"known")
        asset = omni.import_media(self.home, src)["id"]
        new_src = self.root / "new.bin"
        new_src.write_bytes(b"must not be copied")
        new_digest = omni._hash_file(new_src)[0]
        with sqlite3.connect(self.home / "omnifeed.sqlite3") as con:
            con.execute("UPDATE schema_meta SET value='99' WHERE key='schema_version'")
        with closing(sqlite3.connect(self.home / "omnifeed.sqlite3")) as con:
            before = con.execute("SELECT count(*) FROM usage_events").fetchone()[0]
        with self.assertRaises(omni.OmniError):
            omni.import_media(self.home, new_src)
        with self.assertRaises(omni.OmniError):
            omni.record_event(self.home, event_id=str(uuid.uuid4()), asset_id=asset, event_type="played")
        self.assertFalse((self.home / "media" / new_digest[:2] / new_digest).exists())
        with closing(sqlite3.connect(self.home / "omnifeed.sqlite3")) as con:
            after = con.execute("SELECT count(*) FROM usage_events").fetchone()[0]
        self.assertEqual(before, after)

    def test_preflight_rejects_database_sidecar_symlink(self):
        sidecar = self.home / "omnifeed.sqlite3-wal"
        external = self.root / "external-wal"
        external.write_bytes(b"external")
        if sidecar.exists():
            sidecar.unlink()
        sidecar.symlink_to(external)
        with self.assertRaises(omni.OmniError):
            omni.status(self.home)

    def test_empty_token_rejected_before_init_changes_permissions(self):
        token = self.home / "secrets" / omni.TOKEN_NAME
        token.write_bytes(b"")
        os.chmod(self.home, 0o755)
        try:
            with self.assertRaises(omni.OmniError):
                omni.init(self.home)
            self.assertEqual(0o755, stat.S_IMODE(self.home.stat().st_mode))
            self.assertEqual(b"", token.read_bytes())
        finally:
            os.chmod(self.home, 0o700)

    @unittest.skipIf(os.name == "nt", "POSIX permission bits")
    def test_private_modes(self):
        for path in (self.home, self.home / "media", self.home / "secrets", self.home / "omnifeed.sqlite3", self.home / "secrets" / omni.TOKEN_NAME):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700 if path.is_dir() else 0o600)


if __name__ == "__main__":
    unittest.main()
