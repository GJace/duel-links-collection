Spec for the code. Background and rejected options: `HISTORY.md`.

## Goal

1. Scan the Duel Links card collection (Steam, Windows) into a file, unattended.
2. Use that file to check which DuelLinksMeta (DLM) decks I can build (Chrome extension or deck ranker).

## Platform

- Windows PC, Steam client, game in a window (not fullscreen). Runs all day unattended.
- Python:
  - `mss`: screenshots.
  - `pydirectinput` or `pyautogui`: clicks, scrolls.
  - OCR: Windows built-in (`winocr`). Fallback: Tesseract.
  - Image hash (e.g. `imagehash`): thumbnail fingerprints.
- Set process DPI awareness. Screen is scaled.
- All coordinates relative to the game window (title `Yu-Gi-Oh! DUEL LINKS`).

## Game screen

Reference: `Screenshot 2026-11-02 085424.png`.

- Card Catalog screen. Grid: 10 columns, about 5.5 rows visible. Bottom row cut off.
- Thumbnail: count number bottom right. Ignore other badges (red circles, green stars, rarity label).
- Hover does nothing. A click selects the card and fills the left detail panel:
  - Name: plain text under "Owned Card Details".
  - `Owned: a/b/c/d` on the card image: chronicle/prismatic/glossy/normal. Small text: crop and enlarge before OCR.
- Catalog lists owned cards only.
- Same name can appear more than once (alt arts). Each is a separate entry.

## Run setup (manual, before each batch)

- No popups open. PC sleep and screen lock off.
- Same window size every run.
- No pack opening or converting during the run (list order must not change).
- Speed toggle on. Rush: separate batches, later, optional.
- Filter: one rarity. Order: UR, SR, R, N.
- Sort: name, ascending.

## Scan loop (per batch)

1. Screenshot the grid. Fingerprint every visible thumbnail.
2. Find the overlap with the previous screen: match the sequence of fingerprints, not a single card. Skip repeats.
3. For each new card: click it, random delay, OCR name and `Owned` line, save the record.
4. Scroll. Random delay.
5. Stop when a scroll leaves the grid unchanged.

## Checks

- Thumbnail count must equal the sum of `Owned`. If not, log it.
- Fuzzy-match each OCR name against the card list from YGOPRODeck (`https://db.ygoprodeck.com/api/v7/cardinfo.php?format=Duel%20Links`). Download once, store locally (limit 20 req/s, else 1h block). Docs say the Duel Links list is "not 100% accurate": no match there, retry against the full list before logging.
- Names out of alphabetical order: log it (misread or skipped row).
- Logged cards: save the screenshot for manual review.

## Logs

- All logs and review screenshots go in `logs/` in the repo, committed. Synced via git between Mac (dev) and Windows (game).
- One subfolder per run (e.g. `logs/<date>-<batch>/`). Includes the scroll test screenshots.
- Keep screenshots cropped to the grid and detail panel, PNG. Repo size grows with every run.

## Safety

- Clicks only inside the grid area. Convert and Batch Convert are next to it and dismantle cards.
- Before each click, check the screen is still the Card Catalog (e.g. match a fixed region like the "Card Catalog" title). If not, stop.
- Random delays on every action.

## Output

- Append one record per card as it is read (JSONL per batch). Resume from the last record.
- Record:

```json
{"name": "Black Rose Garden", "art": "<thumbnail hash>", "rarity": "UR", "owned": {"chronicle": 0, "prismatic": 0, "glossy": 0, "normal": 2}, "total": 2}
```

- Final `collection.json`: all batches merged.
- Deck checks use total per name (all arts added up; the 3-copy limit counts them together).

## Build order

1-2. Test scripts: `TESTS.md`.
3. Full scan with resume, checks, logging.
4. DLM side: Chrome extension marking owned/missing cards on deck pages (e.g. `https://www.duellinksmeta.com/tier-list/deck-types/Memento`), or a script ranking DLM decks by how many cards I'm missing (DLM frontend loads data from its own JSON API).
