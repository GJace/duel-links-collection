"""Test 3: click. Clicks 10 columns in rows 1, 3 and the cut-off bottom row."""
import time

import config
from common import session, wait, pause

ROWS = (0, 2, 5)
DELAYS_MS = (0, 300, 1000)


def main():
    print("Before you start: the first screen should show a card with alt arts and")
    print("one with several finishes owned (Owned: not all in one slot).")
    with session("click") as (run, game):
        game.set_guard()
        run.save(game.shot(config.SAVE), "before.png", what="before any click")
        for row in ROWS:
            for col in range(config.COLS):
                game.click_cell(col, row)
                t0 = time.monotonic()
                for ms in DELAYS_MS:
                    wait(max(0, t0 + ms / 1000 - time.monotonic()))
                    img = game.shot(config.SAVE)
                    run.save(img, f"r{row + 1}c{col + 1}_{ms}ms.png", col=col, row=row,
                             delay_ms=ms, actual_ms=round((time.monotonic() - t0) * 1000))
                pause(1.0, 2.5)


if __name__ == "__main__":
    main()
