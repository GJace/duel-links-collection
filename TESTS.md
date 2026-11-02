Test scripts to run on the Windows PC before writing the scanner. Goal: after one run of each, the logs hold everything needed to write the full scan.

## Rules for all tests

- Dumb scripts: capture raw data, no analysis. Analysis happens on the Mac from the logs.
- Output in `logs/test-<name>/`: full-resolution PNGs plus `meta.json` (window position and size, DPI scale, screen resolution, timestamps, every action taken).
- Start: game on the Card Catalog, Speed, filter UR, sort by name ascending, no popups.
- After the run: commit and push `logs/`.

## 1. Environment probe

- Find the game window. Record its position, size, DPI scale and screen resolution.
- Screenshot the full screen and the window area.
- Move the mouse to the window's 4 corners, screenshot each (cursor visible) to confirm clicks land where screenshots say.
- Check that the OCR engine loads. Record Python and library versions.

Learn: coordinates, scaling, whether screenshot and mouse coordinates agree.

## 2. Scroll

- One mouse-wheel notch at a time over the grid, screenshot after each, until the grid stops changing (max 50).
- After a few of those scrolls, take extra screenshots at 0, 200, 500, 1000 ms to see whether the list keeps moving after the scroll (inertia).
- Repeat once with 3 notches per scroll.

Learn: rows per notch, consistency, settle time, how the end of the list looks.

## 3. Click

- Click each of the 10 columns in rows 1, 3 and the cut-off bottom row. Screenshot at 0, 300, 1000 ms after each click.
- Pick at least one card with alt arts and one with several finishes owned.

Learn: grid coordinates, detail panel update time, whether clicking the bottom row scrolls the grid, any popup or side effect from a click.

## 4. OCR

- On the click test screenshots: crop name and `Owned` line, run the Windows OCR, raw and enlarged (2x, 3x).
- Save crops plus raw OCR text side by side.
- Also crop each thumbnail's count number and try OCR on it.

Learn: crop regions, best enlargement, OCR error types, whether thumbnail counts need image matching instead of OCR.

## 5. Soak

- Run for several hours while away: click a random card from the first screen every 30-90 s, screenshot every 5 min.
- Flag any screenshot where the "Card Catalog" title is missing.

Learn: disconnects, idle timeouts, daily-reset or event popups, what an unexpected screen looks like.

## Manual notes (no script)

Add to `logs/notes.md`:
- Number of owned cards per rarity, if the game shows it.
- Daily reset time, if known.
- Anything odd seen during the tests.
