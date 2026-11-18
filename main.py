#!/usr/bin/env python3
"""The World in One Image - a poster-style news front page for make.fun's
"Sum up 18 November's world news in one image" (news-image-20261118).

Draws a 1024x1024 newspaper front page for Wednesday 18 November 2026:
a lead story (U.S. strikes on Qeshm Island, Iran), four secondary stories
(Kerch Bridge, Shenzhen summit, Cyclone Xavier, Ebola in DR Congo) and a
ticker (Peltola wins Alaska). Pure Python standard library: a hand-defined
5x7 bitmap font, flat-shape scene illustrations and a hand-rolled PNG
encoder. Deterministic: the same bytes every run.

Run:  python3 main.py        (writes /output/entry.png, or ./entry.png)
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# ------------------------------------------------------------- palette -----

PAPER = (245, 240, 225)
INK = (20, 24, 29)
RED = (193, 39, 45)
BLUE = (20, 64, 107)
TEAL = (13, 110, 119)
SKY = (178, 208, 226)
SEA = (62, 138, 158)
SAND = (219, 186, 122)
ORANGE = (233, 116, 31)
GOLD = (242, 183, 44)
WHITE = (255, 255, 255)
GREY = (105, 104, 98)
LGREY = (186, 180, 164)
BROWN = (122, 82, 48)

# ---------------------------------------------------------------- font -----
# 5x7 bitmap glyphs, 7 rows of 5 pixels each. Every letter the page needs
# is drawn from these grids, so no glyph can come out garbled.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": (".##..", "..#..", "...#.", "...#.", "...#.", "..#..", ".##.."),
    "\u00b7": (".....", ".....", ".....", ".###.", ".###.", ".....", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
}

# -------------------------------------------------------------- canvas -----

class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = (y * self.w + x) * 3
            self.px[o] = c[0]
            self.px[o + 1] = c[1]
            self.px[o + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * self.w + x0) * 3
            self.px[o:o + len(row)] = row

    def rect_outline(self, x, y, w, h, c, t=3):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def fill_circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def circle_outline(self, cx, cy, r, c, t=2):
        steps = max(24, r * 4)
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            self.fill_circle(int(cx + r * math.cos(a)),
                             int(cy + r * math.sin(a)), t, c)

    def fill_ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            f = 1.0 - ((yy - cy) / float(ry)) ** 2
            if f < 0:
                continue
            dx = int(rx * math.sqrt(f))
            self.fill_rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        y0 = max(0, int(min(ys)))
        y1 = min(self.h - 1, int(max(ys)))
        n = len(pts)
        for yy in range(y0, y1 + 1):
            yc = yy + 0.5
            xs = []
            for i in range(n):
                xa, ya = pts[i]
                xb, yb = pts[(i + 1) % n]
                if ya == yb:
                    continue
                if (ya <= yc < yb) or (yb <= yc < ya):
                    xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), yy,
                               int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def line(self, x0, y0, x1, y1, c, t=3):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        r = max(1, t // 2)
        for i in range(steps + 1):
            f = i / steps
            self.fill_circle(int(x0 + (x1 - x0) * f),
                             int(y0 + (y1 - y0) * f), r, c)

    def rows(self):
        return [bytes(self.px[y * self.w * 3:(y + 1) * self.w * 3])
                for y in range(self.h)]

# ---------------------------------------------------------------- text -----

def text_width(text, scale, bold=False, tracking=0):
    if not text:
        return 0
    adv = 6 * scale + (scale if bold else 0) + tracking
    return len(text) * adv - (adv - 5 * scale - (scale if bold else 0))


def draw_text(cv, text, x, y, scale, c, bold=False, tracking=0):
    adv = 6 * scale + (scale if bold else 0) + tracking
    extra = scale if bold else 0
    cx = x
    for ch in text:
        glyph = FONT[ch]
        for gy in range(7):
            row = glyph[gy]
            for gx in range(5):
                if row[gx] == "#":
                    cv.fill_rect(cx + gx * scale, y + gy * scale,
                                 scale + extra, scale, c)
        cx += adv
    return cx - x


def draw_text_centered(cv, text, cx, y, scale, c, bold=False, tracking=0):
    w = text_width(text, scale, bold, tracking)
    return draw_text(cv, text, cx - w // 2, y, scale, c, bold, tracking)


def draw_text_right(cv, text, x_right, y, scale, c, bold=False, tracking=0):
    w = text_width(text, scale, bold, tracking)
    return draw_text(cv, text, x_right - w, y, scale, c, bold, tracking)

# --------------------------------------------------------------- scenes ----

def star_pts(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    return pts


def scene_iran(cv, x, y, w, h):
    """Lead: Qeshm Island struck; jet, burst, drones, radar site."""
    cv.fill_rect(x, y, w, h - 52, SKY)                 # sky
    cv.fill_rect(x, y + h - 52, w, 52, SEA)            # sea
    # island mound
    cv.fill_ellipse(x + 330, y + h - 46, 190, 20, SAND)
    cv.fill_rect(x, y + h - 52, w, 3, INK)             # horizon line
    # explosion burst on the island
    cv.fill_poly(star_pts(x + 330, y + h - 78, 40, 16, n=8, rot=0.3), ORANGE)
    cv.fill_poly(star_pts(x + 330, y + h - 78, 26, 10, n=8, rot=0.7), RED)
    cv.fill_circle(x + 330, y + h - 78, 9, GOLD)
    # fighter jet, nose to the right, upper right
    jx, jy = x + 596, y + 14
    cv.fill_poly([(jx + 152, jy + 20), (jx + 96, jy + 10), (jx + 52, jy + 8),
                  (jx + 44, jy + 8), (jx + 30, jy), (jx + 18, jy + 10),
                  (jx + 12, jy + 20), (jx + 20, jy + 28), (jx + 60, jy + 30),
                  (jx + 100, jy + 28)], INK)          # fuselage + tail fin
    cv.fill_poly([(jx + 88, jy + 24), (jx + 58, jy + 44), (jx + 42, jy + 44),
                  (jx + 64, jy + 21)], INK)           # swept wing
    cv.fill_poly([(jx + 26, jy + 26), (jx + 6, jy + 38), (jx + 20, jy + 38),
                  (jx + 36, jy + 28)], INK)           # tailplane
    for i in range(3):  # speed lines
        cv.fill_rect(jx - 52 + i * 4, jy + 6 + i * 10, 32 - i * 7, 3, INK)
    # three drones flying right toward the radar site
    for dx, dy in ((x + 700, y + 88), (x + 762, y + 74), (x + 806, y + 96)):
        cv.line(dx - 11, dy - 11, dx + 11, dy + 11, INK, 3)
        cv.line(dx - 11, dy + 11, dx + 11, dy - 11, INK, 3)
        cv.fill_rect(dx - 5, dy - 4, 10, 8, INK)
        for sx, sy in ((-13, -13), (13, -13), (-13, 13), (13, 13)):
            cv.fill_circle(dx + sx, dy + sy, 3, INK)
    # radar headland at the far right
    cv.fill_ellipse(x + w - 46, y + h - 44, 42, 16, SAND)
    cv.fill_rect(x + w - 18, y + h - 84, 5, 40, INK)   # mast
    # parabolic dish: an arc opening left, with a feed arm and receiver dot
    dcx, dcy = x + w - 44, y + h - 98
    for i in range(25):
        a = -1.05 + i * (2.1 / 24)
        cv.fill_circle(int(dcx + 17 * math.cos(a)), int(dcy + 26 * math.sin(a)),
                       3, BLUE)
    cv.line(dcx + 8, dcy, dcx - 12, dcy, BLUE, 3)      # feed arm
    cv.fill_circle(dcx - 14, dcy, 4, BLUE)             # receiver
    for r in (12, 22):  # signal arcs
        for i in range(13):
            a = -0.9 + i * 0.15
            cv.fill_circle(int(dcx - 22 - r * math.cos(a)),
                           int(dcy - r * math.sin(a)), 2, BLUE)


def scene_kerch(cv, x, y, w, h):
    """Kerch Bridge: middle road span dropped into the strait."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h - 20, w, 20, SEA)
    deck = y + 22
    # shores
    cv.fill_rect(x, deck + 6, 66, h - 26, SAND)
    cv.fill_rect(x + w - 66, deck + 6, 66, h - 26, SAND)
    # standing deck sections
    cv.fill_rect(x, deck, 168, 7, INK)
    cv.fill_rect(x + w - 168, deck, 168, 7, INK)
    # towers
    for tx in (x + 120, x + w - 128):
        cv.fill_rect(tx, deck - 14, 8, 40, INK)
    # dropped middle span, tilted into the water
    cv.line(x + 172, deck + 4, x + w - 196, deck + 30, INK, 7)
    cv.line(x + w - 196, deck + 30, x + w - 172, deck + 8, INK, 7)
    # splash where the span hit
    sx = x + w // 2
    for dx, dh in ((-26, 10), (-12, 16), (0, 20), (12, 16), (26, 10)):
        cv.line(sx + dx, y + h - 18, sx + dx + (4 if dx > 0 else -4),
                y + h - 18 - dh, WHITE, 3)
    # water ripples
    for i, wx in enumerate((x + 40, x + 300, x + w - 120)):
        cv.line(wx, y + h - 8, wx + 34, y + h - 8, WHITE, 2)


def scene_summit(cv, x, y, w, h):
    """Shenzhen summit: three flags, three chairs, one long table."""
    mid = x + w // 2
    flags = [(mid - 168, "china"), (mid - 28, "russia"), (mid + 112, "usa")]
    for fx, kind in flags:
        cv.fill_rect(fx - 4, y + 2, 3, 34, INK)        # pole
        fw, fh = 62, 26
        if kind == "china":
            cv.fill_rect(fx, y + 2, fw, fh, RED)
            cv.fill_circle(fx + 12, y + 11, 4, GOLD)
            for gx, gy in ((22, 6), (26, 12), (22, 18)):
                cv.fill_circle(fx + gx, y + gy, 2, GOLD)
        elif kind == "russia":
            cv.fill_rect(fx, y + 2, fw, fh // 3, WHITE)
            cv.fill_rect(fx, y + 2 + fh // 3, fw, fh // 3, BLUE)
            cv.fill_rect(fx, y + 2 + 2 * (fh // 3), fw, fh - 2 * (fh // 3), RED)
            cv.rect_outline(fx, y + 2, fw, fh, INK, 1)
        else:
            cv.fill_rect(fx, y + 2, fw, fh, WHITE)
            for i in range(3):
                cv.fill_rect(fx, y + 2 + i * 9, fw, 4, RED)
            cv.fill_rect(fx, y + 2, 26, 13, BLUE)
            for r in range(2):
                for c in range(3):
                    cv.fill_circle(fx + 5 + c * 8, y + 6 + r * 7, 2, WHITE)
            cv.rect_outline(fx, y + 2, fw, fh, INK, 1)
    # three chairs behind one long table
    for cx in (mid - 118, mid, mid + 118):
        cv.fill_rect(cx - 17, y + h - 27, 34, 18, BROWN)
        cv.fill_rect(cx - 17, y + h - 27, 34, 5, INK)
    cv.fill_rect(mid - 190, y + h - 10, 380, 10, INK)  # table
    cv.fill_rect(mid - 190, y + h - 10, 380, 3, BROWN)


def scene_cyclone(cv, x, y, w, h):
    """Cyclone Xavier: spiral storm over small islands and waves."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x, y + h - 14, w, 14, SEA)
    cx, cy = x + 118, y + h // 2 - 2
    # spiral arms: dots along an Archimedean spiral, banded teal/blue
    steps = 260
    for i in range(steps):
        f = i / steps
        ang = f * 5.2 * math.pi
        r = 4 + f * (h // 2 - 2)
        px = int(cx + r * math.cos(ang))
        py = int(cy + r * math.sin(ang) * 0.8)
        col = TEAL if (i // 16) % 2 == 0 else BLUE
        cv.fill_circle(px, py, 3, col)
    cv.fill_circle(cx, cy, 6, PAPER)                   # eye
    cv.circle_outline(cx, cy, 6, INK, 1)
    # islands under the storm
    for ix, iw in ((x + 268, 74), (x + 372, 54)):
        cv.fill_ellipse(ix + iw // 2, y + h - 12, iw // 2, 9, SAND)
        cv.fill_circle(ix + iw // 2, y + h - 22, 4, TEAL)  # palm blob
        cv.line(ix + iw // 2, y + h - 12, ix + iw // 2, y + h - 20, BROWN, 2)
    # wave zigzags
    for wy in (y + h - 6,):
        wx = x + 236
        while wx < x + w - 16:
            cv.line(wx, wy, wx + 8, wy - 4, WHITE, 2)
            cv.line(wx + 8, wy - 4, wx + 16, wy, WHITE, 2)
            wx += 18


AFRICA = [(30, 2), (46, 0), (64, 2), (74, 7), (79, 15), (84, 23), (89, 29),
          (79, 35), (75, 46), (71, 60), (67, 76), (58, 86), (45, 86),
          (39, 72), (35, 58), (31, 47), (27, 41), (31, 35), (25, 29),
          (19, 25), (11, 19), (15, 11), (21, 5)]


def scene_ebola(cv, x, y, w, h):
    """DR Congo Ebola: Africa outline, medical alert badge, UN figures."""
    bx, by, bw, bh = x + 8, y, 92, 56
    pts = [(bx + int(px * bw / 100.0), by + int(py * bh / 88.0))
           for px, py in AFRICA]
    cv.fill_poly(pts, SAND)
    # outline
    for i in range(len(pts)):
        ax, ay = pts[i]
        bx2, by2 = pts[(i + 1) % len(pts)]
        cv.line(ax, ay, bx2, by2, INK, 2)
    # alert badge over the Congo region
    gx, gy = bx + int(0.42 * bw), by + int(0.55 * bh)
    cv.fill_circle(gx, gy, 12, WHITE)
    cv.circle_outline(gx, gy, 12, RED, 3)
    cv.fill_rect(gx - 3, gy - 8, 6, 16, RED)
    cv.fill_rect(gx - 8, gy - 3, 16, 6, RED)
    # the UN figures, big at the right of the map
    tx = x + 128
    draw_text(cv, "11000 CASES", tx, y + 6, 3, INK, bold=True)
    draw_text(cv, "5400 DEAD", tx, y + 34, 3, RED, bold=True)
    draw_text(cv, "- UN", tx + text_width("5400 DEAD ", 3, bold=True),
              y + 34, 3, INK, bold=True)

# ---------------------------------------------------------------- page -----

def panel(cv, x, y, tag, scene_fn, lines):
    w, h = 474, 204
    cv.rect_outline(x, y, w, h, INK, 3)
    cv.fill_rect(x + 12, y + 9, 10, 10, RED)
    draw_text(cv, tag, x + 28, y + 7, 2, RED, bold=True)
    scene_fn(cv, x + 12, y + 26, 450, 56)
    for i, (text, tracking) in enumerate(lines):
        draw_text(cv, text, x + 12, y + 90 + i * 36, 5, INK,
                  tracking=tracking)


def build():
    cv = Canvas(W, H, PAPER)
    cv.rect_outline(10, 10, W - 20, H - 20, INK, 4)

    # --- masthead: the day, huge and unmissable
    draw_text_centered(cv, "THE WORLD IN ONE IMAGE", 512, 22, 3, INK,
                       tracking=4)
    cv.fill_rect(40, 50, 944, 3, INK)
    draw_text_centered(cv, "WEDNESDAY", 512, 58, 8, INK, bold=True)
    draw_text_centered(cv, "18 NOVEMBER 2026", 512, 121, 6, BLUE, bold=True)
    cv.fill_rect(40, 171, 944, 5, INK)
    cv.fill_rect(40, 180, 944, 2, INK)

    # --- lead story: U.S. strikes Iran missile site on Qeshm Island
    cv.rect_outline(28, 190, 968, 330, INK, 3)
    cv.fill_rect(31, 193, 962, 26, RED)
    draw_text(cv, "LEAD STORY", 44, 199, 2, WHITE, bold=True)
    draw_text_right(cv, "MIDDLE EAST", 980, 199, 2, WHITE, bold=True)
    scene_iran(cv, 40, 228, 944, 148)
    draw_text(cv, "U.S. STRIKES IRAN", 40, 384, 5, INK, bold=True)
    draw_text(cv, "MISSILE SITE", 40, 422, 5, INK, bold=True)
    draw_text(cv, "QESHM ISLAND HIT \u00b7 IRANIAN DRONES", 40, 464, 3, BLUE)
    draw_text(cv, "TARGET BAHRAIN & KUWAIT", 40, 489, 3, BLUE)

    # --- 2x2 grid of secondary stories
    panel(cv, 28, 528, "CRIMEA", scene_kerch,
          [("UKRAINE BREAKS", 0), ("KERCH BRIDGE", 0), ("AGAIN", 0)])
    panel(cv, 522, 528, "CHINA", scene_summit,
          [("XI, PUTIN &", 0), ("TRUMP: SUMMIT", 0), ("WEEK IN SHENZHEN", -2)])
    panel(cv, 28, 740, "PACIFIC \u00b7 CATEGORY 5", scene_cyclone,
          [("CYCLONE XAVIER", 0), ("SLAMS COOK", 0), ("ISLANDS", 0)])
    panel(cv, 522, 740, "AFRICA", scene_ebola,
          [("EBOLA DOUBLES IN", -2), ("DR CONGO", 0)])

    # --- bottom ticker: Peltola wins Alaska
    cv.fill_rect(28, 952, 968, 52, INK)
    cv.fill_poly(star_pts(58, 978, 17, 7), GOLD)
    draw_text(cv, "PELTOLA WINS ALASKA - SENATE 56", 88, 959, 3, PAPER,
              bold=True)
    cv.fill_rect(892, 958, 92, 26, BLUE)
    draw_text_centered(cv, "USA", 938, 964, 2, WHITE, bold=True)
    draw_text_centered(cv, "ALL THE NEWS OF ONE DAY \u00b7 18 NOV 2026",
                       512, 986, 2, LGREY)
    return cv


def encode_png(rows, w, h):
    raw = b"".join(b"\x00" + r for r in rows)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def render():
    return encode_png(build().rows(), W, H)


def main():
    png = render()
    out = "/output/entry.png"
    try:
        os.makedirs("/output", exist_ok=True)
    except OSError:
        out = "entry.png"
    if not os.access(os.path.dirname(out) or ".", os.W_OK):
        out = "entry.png"
    with open(out, "wb") as f:
        f.write(png)
    print(f"wrote {out} ({len(png)} bytes)")


if __name__ == "__main__":
    main()
