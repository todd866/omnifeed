# First milestones

The local storage foundation is implemented: content-addressed imports, a private SQLite catalog and idempotent usage events. The end-to-end product milestones below remain pending; TV and PaperLibrary integration plans are documented.

## 1. Establish the shared library

Import a small supplied audio collection plus one RSS/podcast feed. Preserve sources, deduplicate repeated imports and build a default shuffled channel. Demonstrate browse → play → next → resume without hand-editing data. Set storage and preload budgets.

## 2. Prove iPhone behaviour

Test native audio/BLE candidates on Ian’s iPhone before relying on a PWA-only design. Record locked/background playback, track transitions, interruptions, other media apps, offline start and reconnection. CarPlay is a separate follow-up.

## 3. Build the external headphone client (confirmed first hardware scope)

An external player downloads a small pack, verifies it and plays with the network disconnected. Test restart, full storage, interrupted download and stale manifest. AUX is acceptable for this prototype. Add an explicit Omni/iPhone mode experiment, prioritising a wired iPhone input; simultaneous Bose Bluetooth/calls are not required.

## 4. Resolve physical/electrical feasibility

Identify exact QC35 and PCB revision. Measure available volume, battery condition, acoustic clearances, power in playback/control/sync/sleep and temperatures. Trace source selection and buttons. Review USB-C charging/data topology. Select compute and battery only after these measurements.

Gate: no internal installation specification until source switching, power, thermals, fit and charging are demonstrated. A separate add-on battery is an option, not a conclusion.

## 5. Add one real social source

Audit Threads access and prototype a bounded read-only collector. Test login expiry, missing media, duplicate posts, source changes and collection freshness. Keep a manual import path while the adapter matures. Writes come after reliable read/state handling.

## 6. Build and measure the private experience

Compact reader/player, predictable preloading, offline packs and authenticated media. Compare the same content on the same phone at controlled brightness/network conditions. Report battery use, elapsed time, bytes transferred and warm/cold cache state. Do not infer savings merely from architecture.

## Decisions waiting on evidence

MCU vs Linux; one or two batteries; audio injection/switching topology; phone web/native split; hosted database; first full social adapter; source-specific offline playback; codec baseline; channel/library capacity; target runtime and weight.

Transport experiment: benchmark direct local Wi-Fi controls under delayed/unavailable Internet, network changes and sleep/wake; compare optional BLE only if useful. Prove physical playback controls with radios off. Validate wired iPhone audio separately from USB-C charging.
