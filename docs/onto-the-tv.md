# Onto the TV as an Omni subsystem

Decision: Onto the TV should become Omni’s TV playback component. It is not a competing library or an unrelated application. Integration is planned; the current installed app remains unchanged.

## Existing implementation

Reviewed the maintained [Onto the TV repository](https://github.com/todd866/onto-the-tv) and its local source on 20 September 2026.

| Existing module | Role in Omni |
| --- | --- |
| `src/session.js` | Candidate reusable queue/play/pause/seek/resume controller behind an output adapter. |
| `casting/src/renderer.js`, `dlna.js`, `soap.js` | Samsung/DLNA output adapter. |
| `casting/src/server.js`, `pipeline.js` | Local byte-range delivery and media preparation; preserve LAN assumptions. |
| `src/playback-history.js` | Source for a private history importer: versioned JSON, resume, completion and scene bookmarks. |
| `src/taste.js` | Source for preference migration, with explicit mappings for profiles and source IDs. |
| `src/shuffler.js` | Catalogue import/validation boundary; generated HTML is not a stable integration API. |

The project is MIT licensed; retain its notices when extracting code. Review external binaries and their licences separately.

## Shared ownership

Omni owns stable media identity, source provenance, profiles, channels, watch/listen/read history and availability on devices. TV, phone and headphone clients each own their playback transport and transient device state.

Do not share one global queue accidentally: each playback session belongs to an output/device and profile. An explicit handoff can transfer a position; concurrent sessions remain separate.

## Migration constraints

The existing history is keyed by local file path and limited to 500 entries. It contains private paths; changing a filename creates a new key. Omni needs stable media IDs with a private path mapping. Preserve scene bookmarks and existing history before switching writers.

Existing preferences and catalogue have separate versioned formats. Validate them before importing; unknown/corrupt versions fail without altering either store. Do not execute generated player HTML as an import mechanism.

The existing browser watch log is capped and is not precise watch-time accounting. Do not present migrated values as more complete than they are.

## Sequence

1. Establish Omni’s private storage and media/event model.
2. Build an explicit, read-only importer using synthetic fixtures first. Do not automatically scan or migrate real watch history.
3. Add the TV output adapter while leaving the current application operational.
4. Verify stop/switch/seek/resume, stale renderer events and interrupted preparation against existing tests.
5. Switch data ownership only after backups, mapping validation and real-TV checks. Cloud sync is a separate opt-in step.

DLNA serves media on the trusted local network, with different access assumptions from an authenticated cloud API. Do not expose that server to the Internet as an Omni shortcut.
