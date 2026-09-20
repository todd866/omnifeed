# Omnifeed working rules

Read README.md, docs/principles.md and docs/context.md before changing scope.

- FOSS and self-hostable core; public engineering by default. Proprietary hosting is optional.
- Personal runtime data must live outside all Git checkouts. Never commit account cookies, credentials, media, reading/listening/watch history or real private fixtures, including to a private repository.
- The private companion repository is for deployment configuration and private notes, not live data or secrets.
- Run the public-file check before committing; it is a supplemental guard, not proof that a file contains no personal information. Review the exact staged content.
- The first headphone build is an external player into the QC35 AUX jack. Prefer wired audio, Wi-Fi controls and offline physical controls. BLE may serve as an optional control fallback. Calls and internal integration are not first-prototype requirements.
- Onto the TV is intended to become Omni’s TV subsystem. Preserve its working app until a tested integration exists; do not silently copy personal history or configuration into this repository.
- Do not present research proposals as verified hardware behaviour.
