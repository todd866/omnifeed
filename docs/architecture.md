# Proposed architecture

Status: design proposal, not implemented. Vercel/R2 reflect Ian’s preferred direction; exact frameworks, database and compute module are unselected.

FOSS constraint: core functions must run without proprietary hosted services. Vercel/R2 are optional adapters; plan a self-hosted server and object-store alternative. AI features remain optional with an open/local implementation path.

```text
Sources → laptop collectors → normalised library + asset preparation
                                      ↓
                            private API / object storage
                              ↙                 ↘
                    phone/web client        QC35 audio client
                    feed + music            cached music + controls
                              ↘                 ↙
                              sync user state/events
```

## Software responsibilities

Collectors authenticate to each source, ingest incrementally, retain provenance and expose capability limits. Browser sessions stay on the collector machine. The hosted app does not require source account cookies.

The library distinguishes an item (article, post, episode, recording), its source occurrences and its assets/playback options. Two posts linking the same story need not become one lost original. A song found on three stations is one recording with three discovery signals and potentially several playback providers.

Prepare thumbnails, supported audio variants and bounded offline packs before consumption. Track source ID, canonical URL, collection time, original publication time, availability and last successful refresh. Show stale/failed collection honestly.

Optional ranking and summaries augment stored originals. Chronological browsing, search, collections, read/listen history and manual saves must work without an LLM.

## Client responsibilities

Web: compact feed/library, search, saved items, player, download status. Keep reading scroll; bound player/editor surfaces. Preload predictable next content with bounded concurrency and decode images before transitions.

iOS companion (candidate): native audio, local downloads, remote playback commands and CoreBluetooth, with shared web UI where practical. Prove these integrations early. A PWA alone is not assumed sufficient for reliable headphone control or persistent offline audio.

Headphones: a small audio-only client. Local queue, decoder, storage, physical controls, direct Wi-Fi sync and optional BLE remote. No social collectors, browser rendering or recommendation models on the device. Whether this runs an MCU or Linux is open.

## Access and storage

Private means API and media assets both require authorisation. A password on the website must not leave an R2 bucket public. Proposed device enrolment uses revocable device-scoped access; no R2 administrator keys on the headset. Logout clears phone private caches; unpairing offers local device data removal. Offline revocation cannot erase a disconnected device remotely.

Begin with a local database and fixtures; choose hosted persistence once sync needs are proven. R2 stores objects, not the whole transactional application state.

## Writes to source platforms

Later capability: explicit user action → durable action record → adapter → source confirmation. Use idempotency and reconcile unknown outcomes before retrying, so a network failure cannot silently duplicate a post. Initial prototype is read/import/play; no background posting is implied by collection.

## Music availability

Keep discovery metadata separate from playable assets. A provider-backed catalogue track can appear in the app without having a downloadable file the QC35 can decode. Record playback capabilities explicitly. Prove the hardware path with supplied local audio; provider integrations are separate feasibility work.
