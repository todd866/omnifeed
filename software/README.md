# Omnifeed software

Scope: collectors, library, private delivery API, reader/player and optional iOS companion.

Start with a narrow end-to-end slice: import a small local music folder and one RSS/podcast source; browse/search items; play a default shuffled channel; prepare and consume a bounded offline pack. Add a Threads collection experiment separately so source fragility does not block the core library.

Suggested later layout, once implementation starts: `collectors/`, `library/`, `api/`, `web/`, `ios/`. No framework scaffold yet: the native audio/BLE experiment and source audit should inform it.

See [research](research.md), [architecture](../docs/architecture.md), and [device contract](../shared/device-contract.md).
