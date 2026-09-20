# PaperLibrary integration

Source audit, 20 September 2026. PaperLibrary is a planned reading component of Omni; no corpus or reading-history migration has occurred.

## What already exists

The corpus engine exposes command-line search and status with JSON output. Its durable SQLite catalogue records document identity, metadata, local PDF/text locations and some activity/progress fields. Full-text/vector/graph stores are derived and can be rebuilt. This is a useful library/search adapter boundary.

The native reader has richer private state: fractional reading progress, format-aware reading anchors and PDF highlights/notes. A high-water progress fraction is not the same as the current reading location; do not use one in place of the other when opening a book.

PDF annotations can contain quoted passages and personal notes. They belong in private storage, not public fixtures or a cloud manifest by default.

## First bridge

Keep the existing reader and corpus intact. Define a local adapter that returns a small set of resumable items and their supported locator types. The existing app can open local document paths; no dedicated open-at-position Omni deep link was found in the inspected source.

Initially, a feed card can open a selected local document in the existing reader, relying on its existing restore behaviour only where tested. For a guaranteed exact-location handoff, add a deliberate local IPC/CLI API that accepts a validated document ID and locator and returns success/failure. Do not let two apps write the same catalogue or reader settings without a migration design.

Cache only the metadata needed for a suggestion. Do not crawl or upload the whole personal corpus to make “Continue your book?” work.

## Licensing boundary

The corpus code is MIT licensed. The native reader derives from KDE Okular and is marked GPL-2.0-or-later with preserved notices. It is not all MIT. Preserve the separate-program integration initially; audit compatibility and distribution requirements before copying or linking reader code into another component.

## Acceptance checks

- Correct book and supported reading location after an app restart.
- Backward navigation does not get replaced by a historical maximum progress value.
- Missing/renamed/offline document produces an honest unavailable state.
- Dismissing a suggestion leaves feed and reading state untouched.
- No private title, path, annotation or history enters public logs or fixtures.
