# Public code, private installation

The public repository contains reusable code, schemas, synthetic tests and documentation. An optional private companion repository stores installation preferences and deployment notes. Live data and credentials live outside both repositories.

## Local foundation

The first operational installation uses Python’s standard library, SQLite and an owner-only filesystem media store. It needs no Docker daemon, paid cloud service or proprietary runtime dependency.

The runtime home contains the SQLite database, content-addressed media and a file-backed secret directory. Use a path outside Git and outside automatically published document folders. On macOS, `~/Library/Application Support/Omnifeed` is a suitable installation location; on Linux, use a private application data directory.

See [runtime commands](../software/runtime/README.md) for initialization, status and tests. Initialization preserves existing data and credentials. It does not start a web server, publish media, attach source accounts or migrate TV history.

## Boundaries

| Location | Contents |
| --- | --- |
| Public repository | Code, schema, hardware design, docs and synthetic fixtures. |
| Private companion repository | Deployment settings and private notes; no runtime data or secret values. |
| Runtime database | Asset metadata, usage events and device state. |
| Runtime media directory | Imported files, addressed by content hash. |
| Runtime secrets directory | Locally generated or explicitly configured credentials; never printed by status. |

Owner-only files protect against other ordinary users on the same machine. This initial secret backend is **not an encrypted vault** and does not protect against software running as the owner or disk access outside operating-system controls. A hosted deployment needs its own scoped secret manager and authenticated delivery layer; neither is provisioned by local initialization.

## Public release check

Install the supplemental commit hook with `git config core.hooksPath .githooks`. Run `python3 scripts/check_public.py` to inspect tracked index contents. CI repeats the check and runs synthetic tests. The guard blocks common runtime paths, media/database files and some credential signatures; review the staged diff as well. It is not an exhaustive content classifier.

The default check scans all files in the Git index; `--staged` scans only added/changed staged files. Untracked files and unstaged worktree edits are intentionally excluded because they are not the next commit's contents. `.gitignore` alone cannot prevent a forced add. The local private-repository pre-push hook also checks the expected GitHub remote and confirms private visibility; those local hooks must be reinstalled in a new clone.

Do not push runtime backups to either Git repository. Choose encrypted backup storage and retention before importing irreplaceable content. No automatic cloud backup or remote sync is configured yet.
