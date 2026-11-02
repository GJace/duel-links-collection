# All regions are (x0, y0, x1, y1) as fractions of the game window client area.
# Estimated from "Screenshot 2026-11-02 085424.png". Tune after test 1.

WINDOW_TITLE = "Yu-Gi-Oh! DUEL LINKS"
ABORT_VK = 0x78  # F9. Not F12: Steam uses it for screenshots.

GRID = (0.2834, 0.2420, 0.7174, 0.9334)    # the only area where clicks are allowed
NAME = (0.0096, 0.6044, 0.2578, 0.6402)    # card name under "Owned Card Details"
OWNED = (0.1665, 0.4520, 0.2322, 0.4763)   # "Owned: a/b/c/d" on the big card image
TITLE = (0.2690, 0.0384, 0.3555, 0.0743)   # "Card Catalog" title
SAVE = (0.0, 0.0, 0.738, 1.0)              # part of the window kept in saved screenshots

COLS = 10
FULL_ROWS = 5      # rows 0-4 are fully visible, row 5 is cut off
ROWS = 6

# Centre of the first thumbnail and the spacing between thumbnails.
CELL_X0 = 0.3042
CELL_Y0 = 0.3060
CELL_DX = 0.04339
CELL_DY = 0.11562

# Count number box, as offsets from a thumbnail centre: (dx0, dy0, dx1, dy1).
COUNT = (0.0112, 0.0294, 0.0216, 0.0499)

# Random click offset around the thumbnail centre (max, as fractions).
JITTER_X = 0.0048
JITTER_Y = 0.0128

TITLE_DIFF_MAX = 10.0   # mean grey difference (0-255) of the title crop that stops the script
SAME_DIFF = 0.5         # grid crops closer than this count as "unchanged"
