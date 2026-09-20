# Omni as the personal media home

Product direction, 20 September 2026: Omni is the “everything app” for personal media. Existing specialist apps can become components of one experience rather than separate silos.

- Feed: social posts, news, research and other collected material.
- PaperLibrary: books/papers and continued reading, subject to an integration audit.
- Onto the TV: video channels, playback, watch history and resume.
- Music/headphones: channels and local audio playback.

The shared library supplies identity, source information, collections, progress and user preferences. Specialist readers and players keep the controls needed for their media.

## Suggested changes of activity

Ian’s concrete example: while he is infinite scrolling, Omni can suggest “read some of your book”.

Proposed interaction: a small card, “Continue your book?”, showing the chosen book and saved reading position. Continue opens that exact place; dismiss leaves the feed unchanged. Do not claim a chapter or page unless the reader has supplied a valid position.

The app can use an active browsing session and user-set preferences to suggest reading, listening or another saved activity. This is a proposal, not a rule that every session must become productive. Entertainment remains a valid choice.

## Initial behaviour

1. Record foreground active browsing locally, separating idle time from actual interaction.
2. Offer a reading suggestion only when a resumable book is known and suggestions are enabled.
3. Use configurable thresholds, a cooldown and session-level dismissal. Default to restrained prompts; no modal interruption or forced navigation.
4. Let the user pin a current book and turn these suggestions off.
5. Prepare only the likely next reading target within storage/download budgets, so accepting the suggestion feels immediate.

Recommendation logic should begin with understandable rules, not a required cloud model. Private usage events can improve suggestions later. Do not optimise simply for more minutes spent inside Omni.

## Integration requirements

Stable document IDs; a reader-supplied position (page, EPUB location or another format-aware locator); last-read time; open-at-position capability; availability/download state; and an explicit handoff result. Keep actual book titles, content and reading history in private storage.

See the [PaperLibrary source audit](paperlibrary.md). Treat it as a planned component; no data migration or live connection has been performed.
