# Product context

Product decisions captured 20 September 2026. This is a curated project handoff, not a conversation transcript. Earlier design suggestions are hypotheses unless independently verified in the research notes.

## Confirmed direction

Ian wants two connected components: an app that pulls in and organises his media, and a rebuilt QC35 containing a mini-computer acting as an app client. The project is called Omnifeed, or Omni.

The motivation includes poor real-world phone battery endurance, heavyweight social apps, fragmented information, and social video taking over music playback. Battery savings are a goal to measure, not an established result.

## Preferences from the original discussion

- Collect ahead on Ian’s laptop, rather than continuously executing source apps on the phone.
- Publish the private consumption interface using a Vercel/R2 pattern similar to his existing MD3 project. That project has not been inspected here.
- Combine Threads, Instagram, Facebook, articles, scientific material, newsletters, podcasts and music. These are desired sources, not proven integrations.
- Retain originals and source links; organise, deduplicate and optionally rank across sources. Keep a chronological/raw view available.
- Prepare bounded offline collections. Prefer a brief preparation pause followed by smooth navigation.
- Music channels can combine favourites and discoveries from Triple J, RTRFM, FBi and overseas curators. “Ian Radio” was the working name for the music concept.
- Play should start or resume a designated shuffled channel, with no repeated app/library/track selection.
- Social video should remain muted by default; explicit audio should follow a predictable pause/duck/resume policy.
- Retain a route to posting, replying and liking through the personal interface, with truthful queued/confirmed/failed states.
- Personal media deployment first; FOSS throughout and public engineering work by default, as clarified in this task. See the ground rules.

## QC35 preferences

- Replace micro-USB with USB-C; one connector charges the Bose and added player.
- Keep Bose ANC and provide an explicit switch between internal Omni playback and iPhone audio (wired preferred; transport to be investigated). Ian accepts losing call functionality; seamless incoming-call priority is not required.
- Local music files and queues, autonomous Wi-Fi updates, and a phone remote using BLE where appropriate.
- Reuse physical playback controls if feasible. A technician could assemble/install a reviewed design.
- Internal analogue audio was discussed, but no injection point or source-switching mechanism has been verified. Latest clarification: mutually exclusive Omni/iPhone modes are acceptable; simultaneous Bluetooth and internal playback is unnecessary.

## Still to establish

Exact QC35 generation/PCB revision and condition; usable earcup volume; acceptable extra weight; target playback hours; library size and required codecs; first source integrations; existing app/code reuse; Apple developer account/device constraints; installation budget.

Earlier phone specifications, future OS references, battery projections and optimistic build-time estimates are not project facts.

## Latest transport preference

Ian strongly prefers avoiding Bluetooth, especially for audio. Omni playback uses local files and an internal wired audio path. Prefer Wi-Fi for phone control; evaluate BLE only as an optional control fallback. Physical buttons must remain usable without networking. Investigate wired iPhone audio for iPhone mode; normal Bose Bluetooth may remain an optional fallback. No wired USB audio capability is assumed from the USB-C charging modification.

## Confirmed hardware sequence

Build a non-integrated external device into the QC35 audio-in jack first. Get the design working well, then investigate headphone integration. External prototype success does not require internal fit, shared charging or preserved calls.
