# Omnifeed local private runtime

This is a small Python 3 standard-library storage foundation. It keeps personal
usage records and imported media in a local directory outside Git checkouts.
Run it from this directory or use the absolute script path:

```sh
python3 omni.py --home "$HOME/OmnifeedData" init
python3 omni.py --home "$HOME/OmnifeedData" status
python3 omni.py --home "$HOME/OmnifeedData" import-media /path/to/audio.mp3
python3 omni.py --home "$HOME/OmnifeedData" record-event \
  --id 1a07db4e-82a0-4b86-a629-c2b45c1e86aa \
  --asset ASSET_UUID --type played --progress 42 --duration 180
```

`init` is safe to repeat: it preserves records and the generated device token.
The token is never printed by the CLI. Runtime directories use mode `0700` and
files use `0600` on POSIX systems. The token is a plaintext owner-only secret
file, not an encrypted vault; protect the account and disk, and do not commit
the data directory. `status` reports only aggregate counts and byte totals.

Runtime paths are resolved before checking Git ancestry, including symlinked
ancestors. The home itself and managed child paths cannot be symlinks. This
guard does not detect every cloud-synced folder; choose a local private location.

Imports accept regular files, reject symlink inputs, hash content with SHA-256,
and store a single content-addressed copy. Reimporting identical bytes returns
the original asset. Playback/use events require a UUID event ID and are
idempotent; progress and duration must be finite and nonnegative. Events must
refer to an imported asset.

This is local storage only: there is no network service, encryption at rest,
backup, media-source downloader, or UI. Imported files and the device token are
plaintext on disk; filesystem permissions do not encrypt data. The future TV
experience can be added as another Omnifeed client/subsystem using the same
asset and event model.

Run the focused checks with `python3 -m unittest -v` from this directory.
