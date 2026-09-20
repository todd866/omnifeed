# Software research

Checked 20 September 2026. “Verified” below means documented capability, not tested on Ian’s devices.

| Topic | Evidence | Implication / next check |
| --- | --- | --- |
| iPhone Play commands | Apple says a custom player must be the Now Playing app; remote events go to the current or most recent player. [Apple remote events](https://developer.apple.com/documentation/mediaplayer/handling-external-player-events-notifications) | Verified limit: cannot promise Omni globally captures Play from any app state. Test locked, paused, relaunched and after another app plays. |
| CarPlay | Apple supports audio apps and provides an entitlement request process. [CarPlay](https://developer.apple.com/carplay/) | Native audio feasibility and CarPlay entitlement are separate tasks. Do not promise dashboard availability merely because we have an iOS wrapper. |
| Background work | Apple defines specific audio and BLE background modes. [Background execution](https://developer.apple.com/documentation/Xcode/configuring-background-execution-modes) | Candidate native companion; no assumption of unrestricted continuous execution. |
| Apple Music | MusicKit supports authorised catalogue/library access and playback. [MusicKit](https://developer.apple.com/musickit/) | It is a provider playback integration, not evidence of exportable audio for arbitrary hardware. Validate supported playback and offline behaviour separately. |
| App music player | Apple documents an app-specific music queue and background playback with the audio mode. [ApplicationMusicPlayer](https://developer.apple.com/documentation/musickit/applicationmusicplayer) | Useful candidate for provider playback; separate from Omni’s own-file player. |
| Threads | Meta’s official collection documents creating, managing and publishing content. It notes the collection may lag current features. [Meta collection](https://www.postman.com/meta/threads/documentation/dht3nzz/threads-api), [changelog](https://developers.facebook.com/docs/threads/changelog) | Publishing is not proof of access to Ian’s complete personalised home feed. Audit read, reply, like, follow and publishing capabilities individually. |
| Browser offline storage | Browser storage has quotas and eviction policies. [MDN storage](https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria) | Downloaded status must reflect actual files. Test storage pressure and offline relaunch; do not promise an indefinitely retained PWA music library. |
| Private media | R2 buckets are private by default; public access is explicitly enabled. [R2 public buckets](https://developers.cloudflare.com/r2/buckets/public-buckets/) | Keep media private; choose authenticated delivery and test unauthorised requests as well as page login. |

## Source adapter audit to do

For each of Threads, Instagram, Facebook, RSS/podcasts, publications and radio discovery: record supported read operations, authentication, pagination, stable IDs, attachment availability, cache policy, rate limits, incremental sync, write capabilities and failure recovery. Do not assume the same access across Meta products.

Start radio discovery from playlist metadata. Resolve recordings to playback sources separately, preserving station/show attribution. News/research integrations should retain source links and distinguish full text from metadata-only records.

## First platform experiments

1. Own-file audio on an actual iPhone: lock screen, next track, headset commands, interruptions and offline relaunch.
2. BLE control round-trip with a test peripheral: pair, play/next, state updates, disconnection/reconnection. CoreBluetooth is the candidate; current iOS web Bluetooth suitability is unverified.
3. Collector fixture → library → reader, preserving original IDs and provenance across repeated imports.
4. Private media delivery: playback range requests work; unauthenticated object requests fail; expired authorisation can refresh during an authorised download.
