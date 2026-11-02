"""Test 4: OCR on the screenshots saved by test 3. Usage: t4_ocr.py [test-click run folder]"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageOps

import config
from common import session, crop, count_region, ocr, latest_run

TEXT_SCALES = (1, 2, 3)
COUNT_SCALES = (4, 6, 8)
PAD = 20


def prep(img, scale):
    if scale != 1:
        img = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    return ImageOps.expand(img, border=PAD, fill=img.getpixel((0, 0)))


def run_ocr(run, piece, stem, scales, **info):
    for s in scales:
        img = prep(piece, s)
        name = f"{stem}_x{s}"
        img.save(run.dir / f"{name}.png")
        try:
            text, error = ocr(img), None
        except Exception as e:
            text, error = None, repr(e)
        (run.dir / f"{name}.txt").write_text(text or "", encoding="utf-8")
        run.log("ocr", file=f"{name}.png", scale=s, text=text, error=error, **info)


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else latest_run("click")
    meta = json.loads((src / "meta.json").read_text(encoding="utf-8"))
    last = {}
    for a in meta["actions"]:
        if a["action"] == "shot" and "col" in a:
            key = (a["row"], a["col"])
            if key not in last or a["delay_ms"] > last[key]["delay_ms"]:
                last[key] = a

    with session("ocr", need_window=False) as (run, _):
        run.log("source", folder=str(src))
        for (row, col), a in sorted(last.items()):
            img = Image.open(src / a["file"]).convert("RGB")
            tag = f"r{row + 1}c{col + 1}"
            run_ocr(run, crop(img, config.NAME, config.SAVE), f"name_{tag}", TEXT_SCALES,
                    kind="name", source=a["file"])
            run_ocr(run, crop(img, config.OWNED, config.SAVE), f"owned_{tag}", TEXT_SCALES,
                    kind="owned", source=a["file"])

        first = Image.open(src / "before.png").convert("RGB")
        for row in range(config.ROWS):
            for col in range(config.COLS):
                piece = crop(first, count_region(col, row), config.SAVE)
                run_ocr(run, piece, f"count_r{row + 1}c{col + 1}", COUNT_SCALES,
                        kind="count", source="before.png")


if __name__ == "__main__":
    main()
