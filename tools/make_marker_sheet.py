"""Printable A4 sheet with two ArUco markers (DICT_4X4_50, ids 0 and 1) of exactly 50 mm, and a 100 mm check line.

The marker is a black-and-white square pattern that OpenCV finds automatically in a photo; because its real
size is known (50 mm), it gives the millimetres per pixel of the photo. Print at 100 % ("actual size").
Usage: python tools/make_marker_sheet.py docs/group/marker_sheet_A4.pdf
"""
import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DPI = 600
MM = DPI / 25.4                       # pixels per mm at 600 dpi
MARKER_MM = 50.0
W, H = round(210 * MM), round(297 * MM)


def px(mm):
    return round(mm * MM)


def main(out):
    page = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(page)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", px(4))
        small = ImageFont.truetype("DejaVuSans.ttf", px(3))
    except OSError:
        font = small = ImageFont.load_default()
    dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    d.text((px(15), px(12)), "Scale markers for photos of seeds", font=font, fill=0)
    d.text((px(15), px(19)), "Print at 100 % (actual size, no 'fit to page'). Then check: the line below must be "
                             "exactly 100 mm.", font=small, fill=0)
    # 100 mm check line with ticks every 10 mm
    y = px(32)
    d.line((px(15), y, px(115), y), fill=0, width=px(0.4))
    for k in range(11):
        h = px(4) if k in (0, 5, 10) else px(2)
        d.line((px(15 + 10 * k), y - h, px(15 + 10 * k), y), fill=0, width=px(0.3))
    d.text((px(118), y - px(3)), "100 mm", font=small, fill=0)
    for i, (x0, y0) in enumerate(((30, 60), (30, 170))):
        side = px(MARKER_MM)
        m = cv2.aruco.generateImageMarker(dic, i, side)              # 4x4 data + 1 border = 6 modules
        card = (px(x0 - 12), px(y0 - 12), px(x0 + MARKER_MM + 12), px(y0 + MARKER_MM + 22))
        d.rectangle(card, outline=0, width=px(0.2))                   # cutting line (keeps a white margin)
        page.paste(Image.fromarray(m), (px(x0), px(y0)))
        d.text((px(x0), px(y0 + MARKER_MM + 4)), f"id {i}, 50 mm, keep flat",
               font=small, fill=0)
        d.text((px(x0 + MARKER_MM + 20), px(y0 + 10)), "Cut along the thin line,", font=small, fill=0)
        d.text((px(x0 + MARKER_MM + 20), px(y0 + 16)), "keep the white margin.", font=small, fill=0)
    page.save(out, "PDF", resolution=DPI)
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "marker_sheet_A4.pdf")
