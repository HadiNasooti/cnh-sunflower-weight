#!/usr/bin/env python3
"""Build the printable A4 checklist for the main seed photo collection.

Usage: python3 make_checklist.py [output.pdf]
Needs: reportlab, and the DejaVuSans fonts installed on the system.
Every pile gets its own fully written-out list of steps (nothing is
shortened or repeated by reference).
"""
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FONT_DIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", FONT_DIR + "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

PW, PH = A4
LM = 18 * mm
RM = 18 * mm
TOP = PH - 15 * mm
BOT = 20 * mm
CW = PW - LM - RM
BOX = 4.6 * mm
TXT_X = LM + 16 * mm           # where the step text starts

OUT = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/cnh/main_collection_checklist.pdf"

PILES = [(i + 1, 10 + 2 * i) for i in range(15)]   # (number, target g)
SPECIAL = {3, 8, 13}


def style(size, bold=False, leading=None, align=0):
    return ParagraphStyle("s", fontName="DV-B" if bold else "DV", fontSize=size,
                          leading=leading or size * 1.38, alignment=align,
                          textColor=colors.black)


class Doc:
    def __init__(self, path, total=0):
        self.c = canvas.Canvas(path, pagesize=A4)
        self.c.setTitle("Main collection checklist")
        self.total = total
        self.n = 1
        self.y = TOP
        self.cont = None          # function drawing a continuation heading

    # ---------- page handling ----------
    def footer(self):
        c = self.c
        c.setFont("DV", 9)
        c.setFillColor(colors.black)
        c.drawCentredString(PW / 2, 10 * mm, "Page %d of %d" % (self.n, self.total))
        c.drawString(LM, 10 * mm, "Main collection checklist")

    def new_page(self, use_cont=True):
        self.footer()
        self.c.showPage()
        self.n += 1
        self.y = TOP
        if use_cont and self.cont:
            self.cont()

    def ensure(self, h):
        if self.y - h < BOT:
            self.new_page()

    def finish(self):
        self.footer()
        self.c.save()

    # ---------- basic drawing ----------
    def para(self, html, st, x, w, advance=True):
        p = Paragraph(html, st)
        _, h = p.wrap(w, 1000)
        p.drawOn(self.c, x, self.y - h)
        if advance:
            self.y -= h
        return h

    def para_height(self, html, st, w):
        return Paragraph(html, st).wrap(w, 1000)[1]

    def checkbox(self, x, ytop, size=BOX):
        self.c.setLineWidth(1.1)
        self.c.setStrokeColor(colors.black)
        self.c.rect(x, ytop - size, size, size, stroke=1, fill=0)

    def heading(self, text, size=26, rule=True):
        st = style(size, True, size * 1.2)
        self.para(text, st, LM, CW)
        self.y -= 2 * mm
        if rule:
            self.c.setLineWidth(2)
            self.c.line(LM, self.y, PW - RM, self.y)
        self.y -= 5 * mm

    def subheading(self, text, size=14):
        h = self.para_height(text, style(size, True), CW)
        self.ensure(h + 14 * mm)
        self.y -= 2 * mm
        self.c.setFillColor(colors.Color(0.88, 0.88, 0.88))
        self.c.rect(LM, self.y - h - 3 * mm, CW, h + 4 * mm, stroke=0, fill=1)
        self.c.setFillColor(colors.black)
        self.y -= 1.5 * mm
        self.para(text, style(size, True), LM + 2 * mm, CW - 4 * mm)
        self.y -= 4.5 * mm

    # ---------- steps ----------
    def sub_height(self, sub, fsize, w):
        k = sub[0]
        if k == "check":
            return max(self.para_height(sub[1], style(fsize), w - 8 * mm), BOX) + 2 * mm
        if k == "checks2":
            rows = (len(sub[1]) + 1) // 2
            hs = 0
            for r in range(rows):
                hs += max(self.para_height(t, style(fsize), w / 2 - 9 * mm)
                          for t in sub[1][r * 2:r * 2 + 2]) + 2 * mm
            return hs
        if k in ("field", "choice", "box"):
            return 9.5 * mm
        if k == "lines":
            return 9.5 * mm * sub[1]
        if k == "text":
            return self.para_height(sub[1], style(fsize), w) + 1.5 * mm
        raise ValueError(k)

    def draw_sub(self, sub, fsize, x, w):
        c = self.c
        k = sub[0]
        if k == "check":
            h = self.sub_height(sub, fsize, w)
            self.checkbox(x, self.y - 0.4 * mm, 4 * mm)
            self.para(sub[1], style(fsize), x + 7 * mm, w - 8 * mm, advance=False)
            self.y -= h
        elif k == "checks2":
            rows = (len(sub[1]) + 1) // 2
            for r in range(rows):
                items = sub[1][r * 2:r * 2 + 2]
                rh = max(self.para_height(t, style(fsize), w / 2 - 9 * mm) for t in items) + 2 * mm
                for j, t in enumerate(items):
                    cx = x + j * (w / 2)
                    self.checkbox(cx, self.y - 0.4 * mm, 4 * mm)
                    self.para(t, style(fsize), cx + 7 * mm, w / 2 - 9 * mm, advance=False)
                self.y -= rh
        elif k == "field":
            _, label, length, unit = sub
            self.y -= 9.5 * mm
            c.setFont("DV-B", fsize)
            c.drawString(x, self.y + 1.6 * mm, label)
            lx = x + pdfmetrics.stringWidth(label, "DV-B", fsize) + 2 * mm
            c.setLineWidth(0.9)
            c.line(lx, self.y + 1.2 * mm, lx + length * mm, self.y + 1.2 * mm)
            if unit:
                c.setFont("DV", fsize)
                c.drawString(lx + length * mm + 1.5 * mm, self.y + 1.6 * mm, unit)
        elif k == "choice":
            _, label, opts = sub
            self.y -= 9.5 * mm
            c.setFont("DV-B", fsize)
            c.drawString(x, self.y + 1.6 * mm, label)
            ox = x + pdfmetrics.stringWidth(label, "DV-B", fsize) + 6 * mm
            for i, o in enumerate(opts):
                c.drawString(ox, self.y + 1.6 * mm, o)
                ox += pdfmetrics.stringWidth(o, "DV-B", fsize) + 4 * mm
                if i < len(opts) - 1:
                    c.setFont("DV", fsize)
                    c.drawString(ox, self.y + 1.6 * mm, "/")
                    ox += 5 * mm
                    c.setFont("DV-B", fsize)
        elif k == "box":
            _, label = sub
            self.y -= 9.5 * mm
            c.setFont("DV-B", fsize)
            c.drawString(x, self.y + 1.6 * mm, label)
            bx = x + pdfmetrics.stringWidth(label, "DV-B", fsize) + 3 * mm
            self.checkbox(bx, self.y + 1.0 * mm + BOX - 0.6 * mm)
        elif k == "lines":
            for _ in range(sub[1]):
                self.y -= 9.5 * mm
                c.setLineWidth(0.9)
                c.line(x, self.y + 1.2 * mm, x + w, self.y + 1.2 * mm)
        elif k == "text":
            h = self.para(sub[1], style(fsize), x, w)
            self.y -= 1.5 * mm

    def step(self, num, html, subs=(), fsize=11.5, gap=3.2 * mm):
        tw = CW - (TXT_X - LM)
        ph = self.para_height(html, style(fsize), tw)
        # keep the text and its sub-items together on one page
        total = ph + sum(self.sub_height(s, fsize, tw) for s in subs) + gap
        self.ensure(total)
        top = self.y
        self.checkbox(LM, top - 0.3 * mm)
        c = self.c
        if num != "-":
            c.setFont("DV-B", fsize)
            c.drawString(LM + BOX + 1.6 * mm, top - fsize * 0.98, "%s." % num)
        self.para(html, style(fsize), TXT_X, tw)
        for s in subs:
            self.draw_sub(s, fsize, TXT_X, tw)
        self.y -= gap


# ---------------------------------------------------------------------------
def page_before(d):
    d.heading("Before you start", 28)
    d.para("Do these things first. Tick each box when it is done.", style(11.5), LM, CW)
    d.y -= 4 * mm
    F = 11
    d.step("1", "<b>Set up the iPhone.</b>", [
        ("check", "Settings &gt; Camera &gt; Formats &gt; <b>Most Compatible</b>."),
        ("check", "Settings &gt; Camera &gt; <b>Level ON</b> (on an older iPhone: <b>Grid ON</b>)."),
        ("check", "Use the <b>1x lens</b>. Do not use 0.5x or 2x."),
        ("check", "<b>Flash OFF</b>."),
    ], fsize=F, gap=2.2 * mm)
    d.step("2", "<b>Clean white table.</b> In every photo there may ONLY be: "
                "the seeds, the ruler, the printed marker card and the sticky note. "
                "No feet, legs, hands, floor, phone, cup, pen or other objects.", fsize=F, gap=2.2 * mm)
    d.step("3", "<b>Things you need.</b> Put them on the table now:", [
        ("checks2", ["Kitchen scale", "The empty bowl", "The steel ruler",
                     "The printed marker card (cut out, with its white border)",
                     "Sticky notes and a pen", "The bucket with seeds",
                     "This checklist", "A pen to fill in this checklist"]),
    ], fsize=F, gap=2.2 * mm)
    notes = ["P01", "P02", "P03", "P03-R", "P03-T", "P04", "P05", "P06", "P07", "P08",
             "P08-R", "P08-T", "P09", "P10", "P11", "P12", "P13", "P13-R", "P13-T", "P14", "P15"]
    assert len(notes) == 21
    d.step("4", "<b>Write these sticky notes now</b>, one name on each note, in big letters:",
           [("text", "<b>" + ",  ".join(notes) + "</b>"),
            ("check", "<b>21 notes written.</b>")], fsize=F, gap=2.2 * mm)
    d.step("5", "<b>Marker check.</b> Put the ruler on the printed 100 mm line of the marker sheet.",
           [("field", "Line length:", 30, "mm  (must be 100 mm)")], fsize=F, gap=2.2 * mm)
    d.step("6", "<b>Start.</b> Write the time and the light.", [
        ("field", "Start time:", 35, ""),
        ("choice", "Light (circle one):", ["daylight", "room light"]),
    ], fsize=F, gap=2.2 * mm)
    # rules box
    d.y -= 1 * mm
    rules = [
        "Press <b>TARE</b> right before every weighing.",
        "No seed may touch another seed (except in the T photos).",
        "Camera straight down, lens <b>40 cm</b> above the table. Wait until the "
        "crosshair in the camera turns <b>yellow</b>.",
        "Everything must be inside the photo: all seeds, ruler, marker card and note. "
        "And nothing else.",
        "Never clean the seeds. Broken hull pieces stay in.",
    ]
    st = style(11)
    hs = [d.para_height("&bull; " + r, st, CW - 10 * mm) for r in rules]
    title_h = 7 * mm
    boxh = title_h + sum(hs) + 1.4 * mm * len(rules) + 4 * mm
    d.ensure(boxh)
    d.c.setLineWidth(1.8)
    d.c.rect(LM, d.y - boxh, CW, boxh, stroke=1, fill=0)
    d.y -= 2 * mm
    d.c.setFont("DV-B", 12.5)
    d.c.drawString(LM + 4 * mm, d.y - 4.5 * mm, "Rules that always apply")
    d.y -= title_h
    for r in rules:
        d.para("&bull; " + r, st, LM + 5 * mm, CW - 10 * mm)
        d.y -= 1.4 * mm


# ---------------------------------------------------------------------------
def pile_pages(d, num, target):
    name = "P%02d" % num
    special = num in SPECIAL
    head = "PILE %s: target %d g" % (name, target)
    d.cont = lambda: (d.heading(head + " (continued)", 18), None)[1]
    d.heading(head, 30)
    nphotos = 4 if special else 2
    d.para("Sticky note name: <b>%s</b> &nbsp;&nbsp;|&nbsp;&nbsp; Target weight: <b>%d g</b> "
           "&nbsp;&nbsp;|&nbsp;&nbsp; Photos for this pile: <b>%d</b>" % (name, target, nphotos),
           style(11.5), LM, CW)
    d.y -= 2 * mm
    d.para("Remember: press TARE before every weighing. No seed touches another seed. "
           "Phone straight down at 40 cm. Wait for the yellow crosshair.",
           style(10, False), LM, CW)
    d.y -= 3 * mm
    d.subheading("Part 1: Weigh the seeds and take the photos")

    n = 1
    def S(html, subs=(), **kw):
        nonlocal n
        d.step(str(n), html, subs, **kw)
        n += 1

    S("Stir the seeds in the bucket with your hand.")
    S("Nothing on the scale. Press <b>TARE</b>. The scale shows <b>0 g</b>.")
    S("Put the empty bowl on the scale. Press <b>TARE</b>. The scale shows <b>0 g</b>.")
    S("Scoop seeds from the bucket into the bowl until the scale shows about <b>%d g</b> "
      "(1 g more or less is fine)." % target)
    S("Write down the weight of the seeds in the bowl:",
      [("field", "Weight before:", 36, "g")])
    S("Pour all seeds from the bowl onto the white table.")
    S("Spread the seeds with your fingers so that <b>NO seed touches another seed</b>. "
      "Keep them in one compact area.")
    S("Put the ruler flat along the bottom side of the seeds, at least <b>3 cm</b> away from the seeds.")
    S("Put the marker card flat in a corner, at least <b>3 cm</b> away from the seeds.")
    S("Put the sticky note <b>%s</b> at the side, at least <b>3 cm</b> away from the seeds." % name)
    S("Stand the ruler upright next to the seeds. Hold the phone so the back camera lens is at the "
      "<b>40 cm</b> mark. Then lay the ruler flat again in its place.")
    S("Hold the phone straight down at 40 cm. Wait until the crosshair turns <b>yellow</b>. "
      "Check: all seeds, ruler, marker card and note %s are in the picture, and nothing else." % name)
    S("Take <b>PHOTO A</b> of pile %s." % name, [("box", "Photo A taken:")])
    S("Move the phone away from the table. Bring it back to 40 cm, straight down, crosshair yellow.")
    S("Take <b>PHOTO B</b> of pile %s." % name, [("box", "Photo B taken:")])

    if special:
        d.new_page()
        d.subheading("Part 2: Extra photos (only for pile %s)" % name)
        S("Sweep all seeds together with your hand. Spread them again in a new way, "
          "so that no seed touches another seed.")
        S("Replace the sticky note <b>%s</b> with the sticky note <b>%s-R</b>." % (name, name))
        S("Hold the phone straight down at 40 cm, crosshair yellow. Check: all seeds, ruler, "
          "marker card and note %s-R are in the picture, and nothing else. "
          "Take the <b>R PHOTO</b>." % name, [("box", "R photo taken:")])
        S("Push all seeds together with your hand so that they touch each other. "
          "No seed may lie on top of another seed.")
        S("Replace the sticky note <b>%s-R</b> with the sticky note <b>%s-T</b>." % (name, name))
        S("Hold the phone straight down at 40 cm, crosshair yellow. Check: all seeds, ruler, "
          "marker card and note %s-T are in the picture, and nothing else. "
          "Take the <b>T PHOTO</b>." % name, [("box", "T photo taken:")])
        d.new_page()
        d.subheading("Part 3: Weigh again and put the seeds back")
    else:
        d.new_page()
        d.subheading("Part 2: Weigh again and put the seeds back")

    S("Take the empty bowl. Nothing on the scale: press <b>TARE</b>. Put the empty bowl on the "
      "scale. Press <b>TARE</b>. The scale shows <b>0 g</b>.")
    S("Put <b>ALL</b> seeds from the table back into the bowl. Check the table: no seed left.")
    S("Write down the weight of the seeds in the bowl:",
      [("field", "Weight after:", 36, "g")])
    S("If \"before\" and \"after\" differ by more than 1 g, write what happened:",
      [("lines", 1)])
    S("Pour the seeds from the bowl back into the bucket.")
    S("Does pile %s fit in the photo with no seeds touching?" % name,
      [("choice", "Circle one:", ["yes", "no"]),
       ("text", "<b>If NO: stop here, do not do the next piles, and send a message with the "
                "number of this pile (%s).</b>" % name)])
    S("Count the photos you took for pile %s. It should be %d." % (name, nphotos) +
      ("" if not special else " (This pile has the extra R and T photos.)"),
      [("field", "Number of photos taken for this pile:", 20, "(should be %d)" % nphotos)])
    S("Write the time.", [("field", "Time finished:", 40, "")])
    S("Remarks (light changed, seed fell, anything strange):", [("lines", 2)])
    d.cont = None


# ---------------------------------------------------------------------------
def page_upload(d):
    d.heading("Upload the photos", 28)
    d.para("Do this after all piles are done. Use your phone.", style(11.5), LM, CW)
    d.y -= 4 * mm
    n = 1
    def S(html, subs=()):
        nonlocal n
        d.step(str(n), html, subs, fsize=12, gap=4 * mm)
        n += 1
    S("Open the <b>Google Drive</b> app.")
    S("Go to: <b>My Drive &gt; KU Leuven AI 2025-28 &gt; 2026-27_Master &gt; "
      "S1_Applied-AI-Industrial_B30776 &gt; 02_CNH_Data-Collection &gt; 03_Assignment &gt; photos</b>")
    S("Tap <b>+</b> &gt; <b>New folder</b>. Name the folder: <b>main</b>")
    S("Open the folder <b>main</b>.")
    S("Tap <b>+</b> &gt; <b>Upload</b>. Choose <b>all photos of today</b>.")
    S("Count the photos in the folder <b>main</b>.",
      [("field", "Count of photos uploaded:", 25, "(should be 36 if all 15 piles fit)")])
    S("Take a photo of <b>every page</b> of this filled-in checklist and send it.")


def page_summary(d):
    d.heading("Summary table", 28)
    d.para("Copy the numbers from the pile pages into this table.", style(11.5), LM, CW)
    d.y -= 5 * mm
    cols = [("Pile", 22), ("Target (g)", 30), ("Before (g)", 32), ("After (g)", 32),
            ("Photos", 26), ("Fits? (yes/no)", 32)]
    scale = CW / (sum(w for _, w in cols) * mm)
    widths = [w * mm * scale for _, w in cols]
    rowh = 11.5 * mm
    c = d.c
    x0 = LM
    ytop = d.y
    # header
    c.setFillColor(colors.Color(0.88, 0.88, 0.88))
    c.rect(x0, ytop - rowh, CW, rowh, stroke=0, fill=1)
    c.setFillColor(colors.black)
    x = x0
    c.setFont("DV-B", 10.5)
    for (t, _), w in zip(cols, widths):
        c.drawCentredString(x + w / 2, ytop - rowh + 4 * mm, t)
        x += w
    c.setLineWidth(1)
    for i in range(16):
        yy = ytop - rowh * (i + 1)
        c.line(x0, yy, x0 + CW, yy)
    c.line(x0, ytop, x0 + CW, ytop)
    x = x0
    for w in [0] + widths:
        x += w
        c.line(x, ytop, x, ytop - rowh * 16)
    for i, (num, tg) in enumerate(PILES):
        yy = ytop - rowh * (i + 2) + 4 * mm
        c.setFont("DV-B", 12)
        c.drawCentredString(x0 + widths[0] / 2, yy, "P%02d" % num)
        c.setFont("DV", 12)
        c.drawCentredString(x0 + widths[0] + widths[1] / 2, yy, str(tg))
    d.y = ytop - rowh * 16 - 6 * mm
    d.para("Total photos: ________ &nbsp;&nbsp; (should be 36 if all 15 piles fit)", style(11.5), LM, CW)


def page_monday(d):
    d.heading("Monday 19 October", 28)
    n = 1
    d.subheading("Bring these things")
    for t in ["The jar with <b>150 g</b> of seeds for Jia",
              "A small bag with about <b>15 g</b> of seeds for the test",
              "The kitchen scale", "The ruler", "The marker card",
              "Sticky notes", "The laptop"]:
        d.step("-", t, fsize=11.5, gap=2 * mm)
    d.subheading("Meeting")
    d.step("-", "<b>15:00 to 15:30:</b> online meeting with Jia.", fsize=11.5, gap=2 * mm)
    d.new_page(use_cont=False)
    d.heading("Monday 19 October: small test with Jia", 20)
    d.subheading("In class, during the project time (from about 19:30)")
    n = 1
    def S(html, subs=()):
        nonlocal n
        d.step(str(n), html, subs, fsize=11.5, gap=3 * mm)
        n += 1
    S("Write a sticky note: <b>GRR</b>.")
    S("Put a white sheet of paper on the table.")
    S("Spread the <b>15 g</b> of seeds on the white sheet. <b>No seed touches another seed.</b>")
    S("Put the marker card and the note <b>GRR</b> next to the seeds. Nothing else in the picture.")
    S("Hadi takes a photo with <b>Hadi's phone</b>.")
    S("Hadi takes a photo with <b>Jia's phone</b>.")
    S("Jia takes a photo with <b>Jia's phone</b>.")
    S("Jia takes a photo with <b>Hadi's phone</b>.")
    S("Write which photo is which:", [
        ("field", "Photo 1: taken by", 32, "with phone of ______________"),
        ("field", "Photo 2: taken by", 32, "with phone of ______________"),
        ("field", "Photo 3: taken by", 32, "with phone of ______________"),
        ("field", "Photo 4: taken by", 32, "with phone of ______________"),
    ])
    S("Weigh the seeds.", [
        ("field", "Hadi weighs the seeds:", 35, "g"),
        ("field", "Jia weighs the seeds:", 35, "g"),
    ])
    S("Ask CNH the 5 questions from STATUS_AND_PLAN section 7.")


def build(path, total):
    d = Doc(path, total)
    page_before(d)
    for num, tg in PILES:
        d.new_page(use_cont=False)
        pile_pages(d, num, tg)
    d.new_page(use_cont=False)
    page_upload(d)
    d.new_page(use_cont=False)
    page_summary(d)
    d.new_page(use_cont=False)
    page_monday(d)
    d.finish()
    return d.n


if __name__ == "__main__":
    pages = build("/tmp/_count.pdf", 0)
    pages = build(OUT, pages)
    print("pages:", pages, "->", OUT)
