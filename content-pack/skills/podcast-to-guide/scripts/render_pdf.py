#!/usr/bin/env python3
"""Render a structured guide JSON into a CTE-branded PDF.

Input JSON shape:
{
  "title": "...",
  "subtitle": "...",
  "episode_date": "YYYY-MM-DD",
  "source_label": "AI Daily Brief / Spotify",
  "tldr": ["bullet 1", "bullet 2", "bullet 3"],
  "stories": [
    {"headline": "...", "why_it_matters": "...", "details": ["..."]}
  ],
  "tools_mentioned": [{"name": "...", "note": "..."}],
  "builder_takeaways": ["...", "..."],
  "quotes": [{"text": "...", "speaker": "..."}],
  "source_url": "https://...",
  "youtube_url": "https://..."
}

Brand: dark mode, #00B050 accent, DejaVu fonts. See cte-branded-pdf skill.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from reportlab.lib.colors import Color, HexColor
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# Brand
BG = HexColor("#111111")
SURFACE = HexColor("#1A1A1A")
ACCENT = HexColor("#00B050")
TEXT = HexColor("#F5F5F5")
TEXT_70 = Color(0.961, 0.961, 0.961, 0.7)
MUTED = HexColor("#7A7A7A")
BORDER = HexColor("#2A2A2A")
ACCENT_15 = Color(0, 176/255, 80/255, 0.15)

PAGE_W, PAGE_H = LETTER
MARGIN_X = 54
MARGIN_TOP = 54
MARGIN_BOTTOM = 64

FONT_DIR_CANDIDATES = [
    Path.home() / "Library/Fonts",
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/Library/Fonts"),
]

FONTS = {
    "HeadingBold": "DejaVuSansCondensed-Bold.ttf",
    "Body": "DejaVuSans.ttf",
    "BodyBold": "DejaVuSans-Bold.ttf",
    "BodyItalic": "DejaVuSans-Oblique.ttf",
    "Mono": "DejaVuSansMono.ttf",
    "MonoBold": "DejaVuSansMono-Bold.ttf",
}


def register_fonts() -> None:
    for name, fname in FONTS.items():
        for d in FONT_DIR_CANDIDATES:
            p = d / fname
            if p.exists():
                pdfmetrics.registerFont(TTFont(name, str(p)))
                break
        else:
            raise RuntimeError(f"Font not found: {fname}. Install DejaVu fonts.")


def wrap_text(c: canvas.Canvas, text: str, font: str, size: float, max_w: float) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        if c.stringWidth(test, font, size) <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_background(c: canvas.Canvas) -> None:
    c.setFillColor(BG)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def draw_header(c: canvas.Canvas, label: str) -> None:
    c.setFont("MonoBold", 8)
    c.setFillColor(ACCENT)
    c.drawString(MARGIN_X, PAGE_H - MARGIN_TOP + 18, "CUT THE EDGE")
    c.setFont("Mono", 8)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_W - MARGIN_X, PAGE_H - MARGIN_TOP + 18, label.upper())
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(MARGIN_X, PAGE_H - MARGIN_TOP + 8, PAGE_W - MARGIN_X, PAGE_H - MARGIN_TOP + 8)


def draw_footer(c: canvas.Canvas, page_num: int, total: int, source_url: str | None) -> None:
    c.setStrokeColor(BORDER)
    c.setLineWidth(0.5)
    c.line(MARGIN_X, MARGIN_BOTTOM - 18, PAGE_W - MARGIN_X, MARGIN_BOTTOM - 18)
    c.setFont("Mono", 8)
    c.setFillColor(MUTED)
    if source_url:
        url_short = source_url[:80] + ("…" if len(source_url) > 80 else "")
        c.drawString(MARGIN_X, MARGIN_BOTTOM - 32, url_short)
    c.setFont("MonoBold", 8)
    c.setFillColor(ACCENT)
    c.drawRightString(PAGE_W - MARGIN_X, MARGIN_BOTTOM - 32, f"{page_num:02d} / {total:02d}")


class Page:
    """Render content onto a page with a tracked y-cursor and page-break safety."""

    def __init__(self, c: canvas.Canvas, header_label: str):
        self.c = c
        self.header_label = header_label
        self.y = PAGE_H - MARGIN_TOP - 8
        draw_background(c)
        draw_header(c, header_label)

    @property
    def content_width(self) -> float:
        return PAGE_W - 2 * MARGIN_X

    def needs_break(self, needed: float) -> bool:
        return self.y - needed < MARGIN_BOTTOM

    def paragraph(self, text: str, font="Body", size=10.0, color=TEXT_70, leading=15.2,
                  indent=0.0) -> None:
        max_w = self.content_width - indent
        lines = wrap_text(self.c, text, font, size, max_w)
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        for ln in lines:
            self.c.drawString(MARGIN_X + indent, self.y - size, ln)
            self.y -= leading

    def heading(self, text: str, size=20.0, gap_above=10, gap_below=8) -> None:
        self.y -= gap_above
        self.c.setFont("HeadingBold", size)
        self.c.setFillColor(TEXT)
        self.c.drawString(MARGIN_X, self.y - size, text.upper())
        self.y -= size + gap_below

    def subheading(self, text: str, size=13.0, gap_above=8, gap_below=4) -> None:
        self.y -= gap_above
        self.c.setFont("HeadingBold", size)
        self.c.setFillColor(TEXT)
        self.c.drawString(MARGIN_X, self.y - size, text.upper())
        self.y -= size + gap_below

    def bullet(self, text: str, marker="—") -> None:
        self.c.setFont("MonoBold", 10)
        self.c.setFillColor(ACCENT)
        self.c.drawString(MARGIN_X, self.y - 10, marker)
        self.paragraph(text, indent=22)

    def numbered(self, n: int, lead: str, body: str | None = None) -> None:
        self.c.setFont("MonoBold", 11)
        self.c.setFillColor(ACCENT)
        num_str = f"{n:02d}."
        self.c.drawString(MARGIN_X, self.y - 11, num_str)
        # Lead in bold
        lead_lines = wrap_text(self.c, lead, "BodyBold", 10.5, self.content_width - 28)
        self.c.setFont("BodyBold", 10.5)
        self.c.setFillColor(TEXT)
        for i, ln in enumerate(lead_lines):
            self.c.drawString(MARGIN_X + 28, self.y - 11, ln) if i == 0 else \
                self.c.drawString(MARGIN_X + 28, self.y - 11, ln)
            self.y -= 15
        if body:
            self.y -= 2
            self.paragraph(body, indent=28)

    def quote(self, text: str, speaker: str | None = None) -> None:
        self.y -= 6
        self.c.setStrokeColor(ACCENT)
        self.c.setLineWidth(2)
        bar_top = self.y
        # bar drawn after measuring text
        max_w = self.content_width - 16
        lines = wrap_text(self.c, f"“{text}”", "BodyItalic", 10.5, max_w)
        self.c.setFont("BodyItalic", 10.5)
        self.c.setFillColor(TEXT)
        for ln in lines:
            self.c.drawString(MARGIN_X + 16, self.y - 11, ln)
            self.y -= 15
        if speaker:
            self.c.setFont("MonoBold", 9)
            self.c.setFillColor(ACCENT)
            self.c.drawString(MARGIN_X + 16, self.y - 10, f"— {speaker.upper()}")
            self.y -= 14
        bar_bottom = self.y
        self.c.line(MARGIN_X, bar_top, MARGIN_X, bar_bottom + 4)
        self.y -= 6

    def callout(self, label: str, body: str) -> None:
        # Compute box height
        body_lines = wrap_text(self.c, body, "Body", 10, self.content_width - 24)
        box_h = 14 + 14 + len(body_lines) * 15 + 14
        if self.needs_break(box_h):
            return  # caller handles page break
        self.c.setFillColor(SURFACE)
        self.c.rect(MARGIN_X, self.y - box_h, self.content_width, box_h, stroke=0, fill=1)
        # Accent left bar
        self.c.setFillColor(ACCENT)
        self.c.rect(MARGIN_X, self.y - box_h, 3, box_h, stroke=0, fill=1)
        # Label
        self.c.setFont("MonoBold", 9)
        self.c.setFillColor(ACCENT)
        self.c.drawString(MARGIN_X + 12, self.y - 18, label.upper())
        # Body
        self.c.setFont("Body", 10)
        self.c.setFillColor(TEXT)
        cy = self.y - 32
        for ln in body_lines:
            self.c.drawString(MARGIN_X + 12, cy, ln)
            cy -= 15
        self.y -= box_h + 8

    def divider(self) -> None:
        self.y -= 6
        self.c.setStrokeColor(BORDER)
        self.c.setLineWidth(0.5)
        self.c.line(MARGIN_X, self.y, PAGE_W - MARGIN_X, self.y)
        self.y -= 8


def render(data: dict, out_path: Path) -> None:
    register_fonts()
    c = canvas.Canvas(str(out_path), pagesize=LETTER)
    c.setTitle(data.get("title", "Podcast Guide"))
    c.setAuthor("Cut The Edge")

    pages: list[tuple[str, callable]] = []
    source_url = data.get("source_url") or data.get("youtube_url")

    # Page registry: each entry = (label, render_fn(page))
    def build_pages() -> None:
        pages.append(("COVER", _render_cover(data)))
        if data.get("tldr") or data.get("stories"):
            pages.append(("BRIEF", _render_brief(data)))
        if data.get("builder_takeaways") or data.get("tools_mentioned"):
            pages.append(("ACTIONS", _render_actions(data)))
        if data.get("quotes"):
            pages.append(("QUOTES", _render_quotes(data)))

    build_pages()
    total = len(pages)
    for i, (label, fn) in enumerate(pages, start=1):
        page = Page(c, label)
        fn(page)
        draw_footer(c, i, total, source_url)
        c.showPage()
    c.save()


def _render_cover(data: dict):
    def fn(p: Page) -> None:
        p.y = PAGE_H - MARGIN_TOP - 80
        # Tag
        p.c.setFont("MonoBold", 9)
        p.c.setFillColor(ACCENT)
        p.c.drawString(MARGIN_X, p.y, (data.get("source_label") or "PODCAST GUIDE").upper())
        p.y -= 30
        # Title (large, multi-line)
        title = data.get("title", "Untitled Episode")
        for size in (32, 28, 24, 20):
            lines = wrap_text(p.c, title, "HeadingBold", size, p.content_width)
            if len(lines) <= 4:
                break
        p.c.setFont("HeadingBold", size)
        p.c.setFillColor(TEXT)
        for ln in lines:
            p.c.drawString(MARGIN_X, p.y - size, ln.upper())
            p.y -= size * 1.05
        # Subtitle
        if data.get("subtitle"):
            p.y -= 10
            p.paragraph(data["subtitle"], font="BodyItalic", size=12, color=TEXT, leading=18)
        p.y -= 20
        # Meta block
        meta_bits = []
        if data.get("episode_date"):
            meta_bits.append(("DATE", data["episode_date"]))
        if data.get("channel"):
            meta_bits.append(("SOURCE", data["channel"]))
        if data.get("duration_label"):
            meta_bits.append(("DURATION", data["duration_label"]))
        for label, val in meta_bits:
            p.c.setFont("MonoBold", 8)
            p.c.setFillColor(ACCENT)
            p.c.drawString(MARGIN_X, p.y - 10, label)
            p.c.setFont("Body", 10)
            p.c.setFillColor(TEXT)
            p.c.drawString(MARGIN_X + 80, p.y - 10, val)
            p.y -= 18
    return fn


def _render_brief(data: dict):
    def fn(p: Page) -> None:
        if data.get("tldr"):
            p.heading("TL;DR")
            for b in data["tldr"]:
                p.bullet(b)
        if data.get("stories"):
            p.divider()
            p.heading("Top Stories", size=18)
            for i, s in enumerate(data["stories"], start=1):
                if p.needs_break(80):
                    return  # cut off, future improvement: spill page
                p.subheading(s.get("headline", f"Story {i}"), size=12)
                if s.get("why_it_matters"):
                    p.callout("WHY IT MATTERS", s["why_it_matters"])
                for d in s.get("details", []):
                    p.bullet(d)
                p.y -= 4
    return fn


def _render_actions(data: dict):
    def fn(p: Page) -> None:
        if data.get("builder_takeaways"):
            p.heading("Builder Takeaways")
            for i, t in enumerate(data["builder_takeaways"], start=1):
                p.numbered(i, t)
                p.y -= 2
        if data.get("tools_mentioned"):
            p.divider()
            p.heading("Tools & Names", size=18)
            for tool in data["tools_mentioned"]:
                name = tool.get("name", "?")
                note = tool.get("note", "")
                line = f"{name} — {note}" if note else name
                p.bullet(line)
    return fn


def _render_quotes(data: dict):
    def fn(p: Page) -> None:
        p.heading("Notable Quotes")
        for q in data["quotes"]:
            if p.needs_break(60):
                return
            p.quote(q.get("text", ""), q.get("speaker"))
    return fn


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_json", help="Path to structured guide JSON")
    ap.add_argument("-o", "--output", required=True, help="Output PDF path")
    args = ap.parse_args()
    data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    render(data, out)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
