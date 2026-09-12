#!/usr/bin/env python3
"""Render the README demo GIF from real eval output.

The text in the animation is not written for the demo. It is lifted verbatim from
`evals/results/run6-pass/responses.jsonl` — the same baseline and candidate
responses that produced the published numbers. A demo of measured behaviour is
worth more than an illustration of intended behaviour, and it cannot drift away
from what the skill actually does.

    python3 scripts/make_demo_gif.py
    python3 scripts/make_demo_gif.py --case verbatim-error --trial 1

Requires Pillow. Writes assets/demo.gif.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("error: Pillow is required (pip install pillow)", file=sys.stderr)
    raise SystemExit(2)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESPONSES = REPO_ROOT / "evals" / "results" / "run6-pass" / "responses.jsonl"
OUT = REPO_ROOT / "assets" / "demo.gif"

W, H = 1000, 548
PAD_X, PAD_Y = 26, 22
LINE_H = 21
FONT_SIZE = 15
COLS = 74

BG = (15, 23, 42)
CHROME = (30, 41, 59)
PROMPT = (249, 115, 22)
USER = (248, 250, 252)
BODY = (148, 163, 184)
ACCENT = (249, 115, 22)
CODE = (56, 189, 248)
DIM = (100, 116, 139)
RULE = (51, 65, 85)
LABEL = (100, 116, 139)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\consola.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]
BOLD_CANDIDATES = [
    r"C:\Windows\Fonts\consolab.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
]


def load_font(paths: list[str], size: int):
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


FONT = load_font(FONT_CANDIDATES, FONT_SIZE)
BOLD = load_font(BOLD_CANDIDATES, FONT_SIZE)


# --------------------------------------------------------------------------- #
# Text preparation
# --------------------------------------------------------------------------- #

Span = tuple[str, tuple[int, int, int], bool]  # text, colour, bold
Line = list[Span]


def spans(text: str, base: tuple[int, int, int]) -> Line:
    """Split on backticks and bold markers so code and emphasis get their own colour."""
    out: Line = []
    for chunk in re.split(r"(`[^`]*`|\*\*[^*]*\*\*)", text):
        if not chunk:
            continue
        if chunk.startswith("`") and chunk.endswith("`") and len(chunk) > 1:
            out.append((chunk.strip("`"), CODE, False))
        elif chunk.startswith("**") and chunk.endswith("**") and len(chunk) > 3:
            label = chunk.strip("*")
            out.append((label, ACCENT if label.upper() == "TL;DR" else USER, True))
        else:
            out.append((chunk, base, False))
    return out


def wrap(text: str, base: tuple[int, int, int], width: int = COLS) -> list[Line]:
    """Wrap to `width` visible characters, keeping span colours intact."""
    lines: list[Line] = []
    fenced = False
    for para in text.split("\n"):
        # Fenced blocks lose their ``` markers and render as code. A lone backtick
        # on its own line reads as a rendering bug, not as a terminal.
        if para.strip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            lines.append([("  " + para.strip(), CODE, False)] if para.strip() else [])
            continue
        if not para.strip():
            lines.append([])
            continue
        cur: Line = []
        used = 0
        for chunk, colour, bold in spans(para, base):
            for word in re.split(r"(\s+)", chunk):
                if not word:
                    continue
                if used + len(word) > width and used > 0:
                    lines.append(cur)
                    cur, used = [], 0
                    if word.isspace():
                        continue
                cur.append((word, colour, bold))
                used += len(word)
        if cur:
            lines.append(cur)
    return lines


def load_pair(case_id: str, trial: int) -> tuple[str, str, str]:
    if not RESPONSES.exists():
        raise SystemExit(f"error: {RESPONSES} not found — run the evals first")

    found: dict[str, str] = {}
    for raw in RESPONSES.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        row = json.loads(raw)
        if row.get("case_id") == case_id and row.get("trial") == trial and "response" in row:
            found[row["condition"]] = row["response"]

    missing = {"baseline", "candidate"} - found.keys()
    if missing:
        raise SystemExit(f"error: no {', '.join(sorted(missing))} row for {case_id} trial {trial}")

    cases = {
        json.loads(l)["id"]: json.loads(l)["prompt"]
        for l in (REPO_ROOT / "evals" / "cases.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    }
    return cases[case_id], found["baseline"], found["candidate"]


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #


def draw_line(d: ImageDraw.ImageDraw, x: int, y: int, line: Line) -> None:
    for text, colour, bold in line:
        d.text((x, y), text, font=BOLD if bold else FONT, fill=colour)
        x += int(d.textlength(text, font=BOLD if bold else FONT))


def frame(lines: list[Line], badge: str | None, pinned: Line | None = None) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, 34], fill=CHROME)
    for i, colour in enumerate([(239, 68, 68), (234, 179, 8), (34, 197, 94)]):
        d.ellipse([18 + i * 19, 12, 28 + i * 19, 22], fill=colour)
    d.text((88, 9), "tldr — demo", font=FONT, fill=LABEL)

    if badge:
        w = int(d.textlength(badge, font=BOLD)) + 20
        d.rounded_rectangle([W - w - 18, 8, W - 18, 27], 9, fill=ACCENT)
        d.text((W - w - 8, 9), badge, font=BOLD, fill=BG)

    top = 34
    # The question stays pinned. The whole point of the first act is that the answer
    # overflows, and an answer that scrolls the question away leaves the viewer
    # looking at prose with no idea what was asked.
    if pinned:
        d.rectangle([0, top, W, top + 40], fill=(19, 29, 51))
        d.line([0, top + 40, W, top + 40], fill=RULE, width=1)
        draw_line(d, PAD_X, top + 11, pinned)
        top += 41

    y = top + PAD_Y
    for line in lines[-((H - top - PAD_Y * 2) // LINE_H):]:
        if line and line[0][0] == "\x00RULE":
            d.line([PAD_X, y + 10, W - PAD_X, y + 10], fill=RULE, width=1)
        else:
            draw_line(d, PAD_X, y, line)
        y += LINE_H
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default="verbatim-error")
    ap.add_argument("--trial", type=int, default=1)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    prompt, baseline, candidate = load_pair(args.case, args.trial)
    question = " ".join(prompt.split("\n")[0].split())
    # The pin is a single line and must not run off the right edge.
    if len(question) > 86:
        question = question[:85].rstrip() + "…"

    frames: list[Image.Image] = []
    delays: list[int] = []

    def add(lines, badge, ms, n=1, pinned=None):
        for _ in range(n):
            frames.append(frame(lines, badge, pinned))
            delays.append(ms)

    # 1. the question types itself in
    for i in range(0, len(question) + 1, 4):
        add([[("$ ", PROMPT, True), (question[:i] + "\u2588", USER, False)]], None, 40)

    pin: Line = [("$ ", PROMPT, True), (question, USER, False)]
    add([], None, 500, pinned=pin)

    # 2. the default answer arrives, and keeps arriving
    body = wrap(baseline, BODY)
    for i in range(1, len(body) + 1):
        add(body[:i], None, 55, pinned=pin)
    add(body, None, 1600, pinned=pin)

    # 3. /tldr
    tail = body + [[]]
    for i in range(0, 6):
        add(tail + [[("$ ", PROMPT, True), ("/tldr"[:i] + "\u2588", USER, False)]], None, 90, pinned=pin)
    add(tail + [[("$ ", PROMPT, True), ("/tldr", USER, False)]], None, 500, pinned=pin)

    # 4. same question, new shape
    fresh: list[Line] = []
    add(fresh, "TLDR ON", 700, pinned=pin)

    summary, _, detail = candidate.partition("--- detail ---")
    sum_lines = wrap(summary.strip(), USER)
    for i in range(1, len(sum_lines) + 1):
        add(fresh + sum_lines[:i], "TLDR ON", 130, pinned=pin)

    folded = fresh + sum_lines + [[], [("\x00RULE", RULE, False)], []]
    add(folded, "TLDR ON", 800, pinned=pin)

    det_lines = wrap(detail.strip(), DIM)
    for i in range(1, min(len(det_lines), 6) + 1):
        add(folded + det_lines[:i], "TLDR ON", 90, pinned=pin)
    add(folded + det_lines[:6] + [[], [("  \u2026full detail, still there", DIM, False)]],
        "TLDR ON", 2800, pinned=pin)

    frames[0].save(
        args.out,
        save_all=True,
        append_images=frames[1:],
        duration=delays,
        loop=0,
        optimize=True,
        disposal=2,
    )
    size = Path(args.out).stat().st_size / 1024
    print(f"wrote {args.out}")
    print(f"  {len(frames)} frames, {sum(delays) / 1000:.1f}s, {size:.0f}KB")
    print(f"  source: {args.case} trial {args.trial} from run6-pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
