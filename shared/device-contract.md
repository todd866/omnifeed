# App–device contract sketch

Status: proposed behaviour, not an implemented API or fixed wire format. Version the eventual protocol so the app and firmware can evolve independently.

## Objects

- Recording: stable Omni ID, title/artist/album, duration, source identifiers and discovery provenance.
- Audio asset: immutable asset ID, codec/container, size, hash and sample properties; compatible devices; authorised download capability. URLs are temporary access details, not identity.
- Channel: ID, title, revision and eligible recording IDs. Headphones receive only device-playable entries; unavailable items retain a reason in the main library.
- Pack: versioned snapshot, asset list, byte budget and channel membership. The current pack remains playable until its replacement is complete and verified.
- Device state: device ID, software/protocol version, capabilities, free storage, active pack, playback position and sync status.

## Sync

1. Enrol the device with scoped revocable access.
2. Fetch a compatible manifest and available storage requirement.
3. Download missing assets to temporary files, resume where supported and verify length/hash.
4. Atomically activate a complete pack. Interrupted sync keeps the previous pack usable.
5. Remove obsolete unpinned assets only after activation; never remove the active track.
6. Upload uniquely identified listening events; retries must not double count plays.

Manifest revisions order library updates. Device events retain their own sequence and playback-session IDs; do not order everything by wall clock alone. Device availability differs from a track’s existence in the main library.

## Controls

PLAY resumes or starts the default locally playable shuffled channel. PAUSE, NEXT, PREVIOUS, SET_CHANNEL and SET_VOLUME operate locally. Report empty/download-needed state instead of pretending playback started. Acknowledgements carry command IDs; state reports are authoritative. Use bounded command expiry so a delayed network PLAY does not unexpectedly resume hours later.

Persist queue order, position and shuffle state across restart. Physical controls work without the phone. BLE and Wi-Fi commands must converge on the same player state machine rather than running competing queues.

Two source modes: OMNI (internal local player) and IPHONE (external iPhone audio; wired preferred, interface unselected). An explicit switch selects the source; its physical/electrical implementation remains open. Switching to IPHONE pauses and saves the local queue. Returning to OMNI restores the queue ready for Play. Report actual source state; measure source-switch delay and, if optional Bluetooth is used, its reconnection delay. Call functionality and automatic interruption/resume are not required.

## Control transport priorities

Prefer authenticated direct local Wi-Fi control when both devices can reach one another; the cloud must not be required for nearby Play/Next. Evaluate Wi-Fi setup, discovery, sleep/wake latency and power, plus away-from-home operation (hotspot or device access point, not yet selected). BLE may be an optional low-bandwidth control fallback, never a required audio transport. Physical controls remain the reliable offline baseline. Do not assume Wi-Fi is inherently more reliable without measurements.
