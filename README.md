# Omnifeed

**Omni** is a private personal media library and reader, with a companion audio client built into Ian’s Bose QC35 headphones.

Status: project setup and feasibility research, 20 September 2026. No application, firmware, circuit, or deployment has been implemented yet.

## Two components

- [Software](software/README.md): collect, organise, search and consume social posts, articles, research, music and podcasts. Prepare content ahead of time for fast, offline use.
- [Hardware](hardware/README.md): rebuild the QC35 with an autonomous music player, storage, Wi-Fi sync, phone control, an Omni/iPhone source switch and one USB-C charging port.

The app owns the library and discovery. The headphones own local playback. They should remain useful with the phone disconnected and Wi-Fi unavailable.

## Start here

1. [Product context](docs/context.md): what Ian wants and what remains undecided.
2. [Architecture](docs/architecture.md): proposed responsibilities and boundaries.
3. [First milestones](docs/roadmap.md): small experiments before committing to hardware or infrastructure.
4. [App–headphone interface](shared/device-contract.md): draft sync and playback contract.
5. [Software sources](software/research.md) and [hardware sources](hardware/research.md): evidence and unresolved questions.
6. [Ground rules](docs/principles.md): FOSS, public development, self-hosting and ambitious media handling.

Working name: Omnifeed; short name: Omni. Naming does not imply domain or trademark availability has been checked.
