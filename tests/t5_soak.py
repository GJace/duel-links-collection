"""Test 5: soak. Random click every 30-90 s, screenshot every 5 min. Usage: t5_soak.py [--hours N]"""
import argparse
import random
import time

import config
from common import session, wait

CLICK_EVERY = (30, 90)
SHOT_EVERY = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=4.0)
    hours = ap.parse_args().hours

    with session("soak") as (run, game):
        game.set_guard()
        end = time.monotonic() + hours * 3600
        next_shot = time.monotonic()
        next_click = time.monotonic() + random.uniform(*CLICK_EVERY)
        n = 0
        while time.monotonic() < end:
            now = time.monotonic()
            if now >= next_shot:
                n += 1
                next_shot = now + SHOT_EVERY
                d = game.title_diff()
                flag = d > config.TITLE_DIFF_MAX
                suffix = "_FLAG" if flag else ""
                run.save(game.shot(config.SAVE), f"shot_{n:03d}{suffix}.png",
                         title_diff=round(d, 2), title_missing=flag)
                if flag:
                    run.save(game.shot(), f"shot_{n:03d}{suffix}_full.png", what="full window")
            if now >= next_click:
                game.click_cell(random.randrange(config.COLS), random.randrange(config.FULL_ROWS))
                next_click = time.monotonic() + random.uniform(*CLICK_EVERY)
            wait(1)


if __name__ == "__main__":
    main()
