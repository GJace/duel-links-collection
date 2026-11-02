"""Shared helpers for the test scripts. Windows only."""
import ctypes
import json
import os
import platform
import random
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


def set_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


set_dpi_aware()  # before pyautogui is imported

import mss
import pyautogui
import win32gui
from PIL import Image, ImageChops, ImageDraw, ImageStat

import config

pyautogui.FAILSAFE = True  # mouse into a screen corner aborts
pyautogui.PAUSE = 0

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "logs"
FULL = (0.0, 0.0, 1.0, 1.0)
NOTCH = 120
ABORT_HELP = "Abort: hold F9 for a second, or throw the mouse into a screen corner."


class Abort(Exception):
    pass


class GuardError(Exception):
    pass


STOPS = (Abort, GuardError, pyautogui.FailSafeException)


def check_abort():
    if ctypes.windll.user32.GetAsyncKeyState(config.ABORT_VK) & 0x8000:
        raise Abort("abort key pressed")


def wait(seconds):
    end = time.monotonic() + seconds
    while True:
        check_abort()
        left = end - time.monotonic()
        if left <= 0:
            return
        time.sleep(min(0.05, left))


def pause(lo, hi):
    wait(random.uniform(lo, hi))


# ---- images and regions ----

def crop(img, region, area=FULL):
    """Crop a window-fraction region from an image that covers `area` of the window."""
    ax0, ay0, ax1, ay1 = area
    x0, y0, x1, y1 = region
    w, h = img.size
    return img.crop((
        round((x0 - ax0) / (ax1 - ax0) * w),
        round((y0 - ay0) / (ay1 - ay0) * h),
        round((x1 - ax0) / (ax1 - ax0) * w),
        round((y1 - ay0) / (ay1 - ay0) * h),
    ))


def diff(a, b):
    if a.size != b.size:
        return 255.0
    d = ImageChops.difference(a.convert("L"), b.convert("L"))
    return ImageStat.Stat(d).mean[0]


def mark(img, x, y):
    d = ImageDraw.Draw(img)
    d.line((x - 12, y, x + 12, y), fill=(255, 0, 0), width=2)
    d.line((x, y - 12, x, y + 12), fill=(255, 0, 0), width=2)
    d.ellipse((x - 6, y - 6, x + 6, y + 6), outline=(255, 0, 0), width=2)


def cell_center(col, row):
    return config.CELL_X0 + col * config.CELL_DX, config.CELL_Y0 + row * config.CELL_DY


def count_region(col, row):
    cx, cy = cell_center(col, row)
    dx0, dy0, dx1, dy1 = config.COUNT
    return cx + dx0, cy + dy0, cx + dx1, cy + dy1


def inside(region, fx, fy):
    x0, y0, x1, y1 = region
    return x0 <= fx <= x1 and y0 <= fy <= y1


def ocr(img):
    import winocr
    return winocr.recognize_pil_sync(img, "en")["text"]


# ---- game window ----

def find_hwnd():
    found = []

    def cb(h, _):
        if win32gui.IsWindowVisible(h) and win32gui.GetWindowText(h) == config.WINDOW_TITLE:
            found.append(h)

    win32gui.EnumWindows(cb, None)
    if not found:
        sys.exit(f"Window '{config.WINDOW_TITLE}' not found.")
    return found[0]


def client_rect(hwnd):
    _, _, w, h = win32gui.GetClientRect(hwnd)
    x, y = win32gui.ClientToScreen(hwnd, (0, 0))
    return x, y, w, h


class Game:
    def __init__(self):
        self.hwnd = find_hwnd()
        win32gui.ShowWindow(self.hwnd, 9)  # restore if minimised
        try:
            win32gui.SetForegroundWindow(self.hwnd)
        except Exception:
            pass
        time.sleep(0.5)
        self.rect = client_rect(self.hwnd)
        self.sct = mss.mss()
        self.run = None
        self.title_ref = None

    def info(self):
        x, y, w, h = self.rect
        l, t, r, b = win32gui.GetWindowRect(self.hwnd)
        dpi = ctypes.windll.user32.GetDpiForWindow(self.hwnd)
        return {
            "window_title": config.WINDOW_TITLE,
            "client_rect": {"x": x, "y": y, "w": w, "h": h},
            "outer_rect": {"x": l, "y": t, "w": r - l, "h": b - t},
            "dpi": dpi,
            "dpi_scale": dpi / 96,
            "screen_resolution": {
                "w": ctypes.windll.user32.GetSystemMetrics(0),
                "h": ctypes.windll.user32.GetSystemMetrics(1),
            },
            "monitors": self.sct.monitors,
        }

    def check_window(self):
        check_abort()
        if client_rect(self.hwnd) != self.rect:
            raise GuardError("game window moved or resized")

    def point(self, fx, fy):
        x, y, w, h = self.rect
        return x + round(fx * w), y + round(fy * h)

    # screenshots

    def grab(self, x, y, w, h):
        raw = self.sct.grab({"left": x, "top": y, "width": w, "height": h})
        return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")

    def shot(self, region=FULL):
        self.check_window()
        x, y, w, h = self.rect
        x0, y0, x1, y1 = region
        return self.grab(x + round(x0 * w), y + round(y0 * h),
                         round((x1 - x0) * w), round((y1 - y0) * h))

    def screen(self):
        return self.grab(*self._monitor0())

    def _monitor0(self):
        m = self.sct.monitors[0]
        return m["left"], m["top"], m["width"], m["height"]

    # title guard

    def set_guard(self):
        self.title_ref = self.shot(config.TITLE)
        self.run.save(self.title_ref, "title_ref.png", what="Card Catalog title reference")

    def title_diff(self):
        return diff(self.shot(config.TITLE), self.title_ref)

    # input

    def move(self, fx, fy):
        self.check_window()
        px, py = self.point(fx, fy)
        pyautogui.moveTo(px, py, duration=random.uniform(0.15, 0.4))
        return px, py

    def hover_grid(self):
        x0, y0, x1, y1 = config.GRID
        fx = (x0 + x1) / 2 + random.uniform(-0.05, 0.05)
        fy = (y0 + y1) / 2 + random.uniform(-0.05, 0.05)
        return self.move(fx, fy)

    def scroll(self, notches):
        """Positive scrolls the list down, negative up."""
        px, py = self.hover_grid()
        pause(0.1, 0.3)
        self.check_window()
        pyautogui.scroll(-NOTCH * notches)
        self.run.log("scroll", notches=notches, x=px, y=py)

    def click(self, fx, fy, **info):
        """The only click function. Refuses anything outside the grid."""
        if not inside(config.GRID, fx, fy):
            raise GuardError(f"click outside the grid refused: {fx:.4f}, {fy:.4f}")
        if self.title_ref is None:
            raise GuardError("click refused: title guard not set")
        self.check_window()
        d = self.title_diff()
        if d > config.TITLE_DIFF_MAX:
            raise GuardError(f"'Card Catalog' title differs (diff {d:.1f}): screen changed")
        px, py = self.point(fx, fy)
        hit = win32gui.WindowFromPoint((px, py))
        if not hit or win32gui.GetAncestor(hit, 2) != self.hwnd:
            raise GuardError("another window covers the click point")
        pyautogui.moveTo(px, py, duration=random.uniform(0.15, 0.4))
        pause(0.05, 0.2)
        pyautogui.mouseDown()
        try:
            time.sleep(random.uniform(0.05, 0.12))
        finally:
            pyautogui.mouseUp()
        self.run.log("click", fx=round(fx, 5), fy=round(fy, 5), x=px, y=py,
                     title_diff=round(d, 2), **info)

    def click_cell(self, col, row):
        cx, cy = cell_center(col, row)
        fx = cx + random.uniform(-1, 1) * config.JITTER_X
        fy = cy + random.uniform(-1, 1) * config.JITTER_Y
        self.click(fx, fy, col=col, row=row)


# ---- run log ----

class Run:
    def __init__(self, name, info=None):
        self.start = datetime.now()
        self.dir = LOGS / f"test-{name}" / self.start.strftime("%Y%m%d-%H%M%S")
        self.dir.mkdir(parents=True)
        self.t0 = time.monotonic()
        self.meta = {"test": name, "started": self.start.isoformat(timespec="milliseconds"),
                     "status": "running", **(info or {}), "actions": []}
        self.write_meta()

    def write_meta(self):
        tmp = self.dir / "meta.tmp"
        tmp.write_text(json.dumps(self.meta, indent=1), encoding="utf-8")
        os.replace(tmp, self.dir / "meta.json")

    def log(self, action, **data):
        self.meta["actions"].append({
            "t": datetime.now().isoformat(timespec="milliseconds"),
            "dt": round(time.monotonic() - self.t0, 3),
            "action": action, **data})
        self.write_meta()

    def save(self, img, filename, **info):
        img.save(self.dir / filename)
        self.log("shot", file=filename, **info)

    def finish(self, status):
        self.meta["status"] = status
        self.meta["ended"] = datetime.now().isoformat(timespec="milliseconds")
        self.write_meta()


@contextmanager
def session(name, need_window=True):
    print(ABORT_HELP)
    game = Game() if need_window else None
    info = game.info() if game else {}
    info.update(python=sys.version, platform=platform.platform())
    run = Run(name, info)
    if game:
        game.run = run
    print(f"Logging to {run.dir}")
    try:
        yield run, game
        run.finish("done")
        print("Done. Commit and push logs/ yourself.")
    except STOPS as e:
        print(f"STOPPED: {e!r}")
        run.finish(f"stopped: {e!r}")
        if game:
            for label, fn in (("window", game.shot), ("screen", game.screen)):
                try:
                    run.save(fn(), f"stopped_{label}.png", what="screen at stop")
                except Exception:
                    pass
        sys.exit(1)
    except KeyboardInterrupt:
        run.finish("interrupted")
        sys.exit(1)
    except Exception:
        run.finish("error: " + traceback.format_exc())
        raise


def latest_run(name):
    runs = sorted(LOGS.glob(f"test-{name}/*/meta.json"))
    if not runs:
        sys.exit(f"No logs found for test-{name}.")
    return runs[-1].parent
