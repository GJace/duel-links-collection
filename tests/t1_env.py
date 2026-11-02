"""Test 1: environment probe. Needs the game window; moves the mouse, never clicks."""
import sys
import traceback
from importlib import metadata

import win32gui

import config
from common import session, wait, crop, mark, ocr


def versions():
    out = {"python": sys.version}
    for pkg in ("mss", "pyautogui", "Pillow", "winocr", "pywin32"):
        try:
            out[pkg] = metadata.version(pkg)
        except Exception as e:
            out[pkg] = f"missing: {e!r}"
    return out


def main():
    with session("env") as (run, game):
        run.log("versions", **versions())
        gx, gy, w, h = game.rect
        o = game.info()["outer_rect"]

        run.save(game.screen(), "screen.png", what="full screen")
        window = game.shot()
        run.save(window, "window.png", what="client area")
        run.save(game.grab(o["x"], o["y"], o["w"], o["h"]), "window_outer.png", what="outer window")

        corners = {
            "top_left": (2 / w, 2 / h),
            "top_right": (1 - 2 / w, 2 / h),
            "bottom_left": (2 / w, 1 - 2 / h),
            "bottom_right": (1 - 2 / w, 1 - 2 / h),
        }
        for name, (fx, fy) in corners.items():
            px, py = game.move(fx, fy)
            wait(0.5)
            cx, cy = win32gui.GetCursorPos()
            img = game.shot()
            mark(img, cx - gx, cy - gy)
            run.save(img, f"corner_{name}.png", what="red cross = cursor position",
                     target=[px, py], cursor=[cx, cy])

        try:
            piece = crop(window, config.NAME)
            text = ocr(piece.resize((piece.width * 2, piece.height * 2)))
            run.log("ocr_check", ok=True, text=text)
        except Exception:
            run.log("ocr_check", ok=False, error=traceback.format_exc())


if __name__ == "__main__":
    main()
