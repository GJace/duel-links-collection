"""Test 2: scroll. Moves the mouse over the grid and uses the wheel. Never clicks."""
import time

import config
from common import session, wait, pause, diff

MAX_SCROLLS = 50
INERTIA_SCROLLS = (3, 4, 5)
INERTIA_MS = (0, 200, 500, 1000)


def grid(game):
    return game.shot(config.GRID)


def scroll_pass(run, game, tag, notches):
    prev = grid(game)
    run.save(prev, f"{tag}_000.png", scroll=0, notches=notches)
    same = 0
    for n in range(1, MAX_SCROLLS + 1):
        game.scroll(notches)
        t0 = time.monotonic()
        if n in INERTIA_SCROLLS:
            for ms in INERTIA_MS:
                wait(max(0, t0 + ms / 1000 - time.monotonic()))
                img = grid(game)
                run.save(img, f"{tag}_{n:03d}_{ms}ms.png", scroll=n, notches=notches,
                         delay_ms=ms, actual_ms=round((time.monotonic() - t0) * 1000))
        else:
            pause(1.2, 1.8)
            img = grid(game)
            run.save(img, f"{tag}_{n:03d}.png", scroll=n, notches=notches)
        same = same + 1 if diff(img, prev) < config.SAME_DIFF else 0
        if same == 2:
            run.log("end_reached", tag=tag, scroll=n)
            return
        prev = img
    run.log("max_scrolls_reached", tag=tag)


def back_to_top(run, game):
    prev = grid(game)
    for i in range(100):
        game.scroll(-5)
        pause(1.0, 1.5)
        img = grid(game)
        done = diff(img, prev) < config.SAME_DIFF
        prev = img
        if done:
            break
    run.log("back_to_top", scrolls=i + 1)


def main():
    with session("scroll") as (run, game):
        scroll_pass(run, game, "n1", 1)
        back_to_top(run, game)
        scroll_pass(run, game, "n3", 3)


if __name__ == "__main__":
    main()
