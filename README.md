# duel-links-collection
## Running the tests

On the Windows PC. Game in a window on the Card Catalog: Speed on, filter UR, sort name ascending, no popups. Spec: `TESTS.md`.

- Install: `pip install -r requirements.txt`
- Run from the repo root, in this order:
  1. `python tests\t1_env.py`
  2. `python tests\t2_scroll.py`
  3. `python tests\t3_click.py`
  4. `python tests\t4_ocr.py [logs\test-click\<run>]` (default: latest test 3 run)
  5. `python tests\t5_soak.py [--hours 4]`
- Check the regions in `tests/config.py` against the shots from test 1 before test 3.
- Abort: hold F9, or move the mouse into a screen corner. A script also stops if the "Card Catalog" title changes.
- Logs go to `logs/test-<name>/<timestamp>/`. The scripts never commit. After each test: commit and push `logs/`.
- Manual notes go in `logs/notes.md`.
