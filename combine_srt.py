#!/usr/bin/env python3
"""Combine split SRT files into single files with proper timestamp renumbering.

Excludes WhisperJAV credit cues and closing-credit-slot cues from offset
calculations so timestamps chain correctly across parts.
"""

import re
from pathlib import Path

BASE = Path(".")
PARTS = [
    "HUNTA-010 - Lulustream.part01",
    "HUNTA-010 - Lulustream.part02",
    "HUNTA-010 - Lulustream.part03",
]

# Text patterns that indicate a credit cue
CREDIT_TEXTS = {
    "subs by whisperjav",
    "whisperjav 1.9.5 | balanced/aggressive",
}

# Closing credit slot timestamp (WhisperJAV puts credits here)
CLOSING_CREDIT_START = 23 * 3600 + 59 * 60 + 58  # 23:59:58


def parse_time(s):
    """Parse SRT timestamp like '00:00:02,800' -> total seconds (float)."""
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0


def format_time(seconds):
    """Format total seconds -> SRT timestamp '00:00:02,800'."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(path, lang):
    """Parse an SRT file into a list of (start_sec, end_sec, text) entries.
    Skips credit cues and closing-credit-slot cues.
    """
    text = path.read_text(encoding="utf-8")
    entries = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        ts_line = lines[1]
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", ts_line)
        if not m:
            continue
        start = parse_time(m.group(1))
        end = parse_time(m.group(2))
        body = "\n".join(lines[2:])

        # Skip credit cues by text
        body_lower = body.strip().lower()
        if body_lower in CREDIT_TEXTS:
            continue

        # Skip closing credit index 9999
        try:
            idx = int(lines[0].strip())
            if idx == 9999:
                continue
        except ValueError:
            pass

        # Skip cues in the closing credit slot (23:59:58+)
        # WhisperJAV uses this slot for credits; English SRTs sometimes
        # have translated dialogue bleed into this slot
        if start >= CLOSING_CREDIT_START:
            continue

        entries.append((start, end, body))
    return entries


def combine(lang):
    """Combine all parts for a given language suffix into one SRT."""
    offset = 0.0
    all_entries = []
    total_cues = 0

    for part in PARTS:
        path = BASE / f"{part}.{lang}.srt"
        if not path.exists():
            print(f"WARNING: {path} not found, skipping")
            continue
        entries = parse_srt(path, lang)
        for start, end, body in entries:
            all_entries.append((start + offset, end + offset, body))
            total_cues += 1
        if entries:
            offset = entries[-1][1]
            print(f"  {part}: {len(entries)} cues, ends at {format_time(entries[-1][1])}, next offset {format_time(offset)}")
        else:
            print(f"  {part}: 0 cues")

    if not all_entries:
        print("No entries to write!")
        return None

    out_name = f"HUNTA-010 - Lulustream.combined.{lang}.srt"
    with open(out_name, "w", encoding="utf-8") as f:
        for i, (start, end, body) in enumerate(all_entries, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{body}\n\n")

    print(f"\nWrote {out_name}: {total_cues} total cues")
    print(f"Total duration: {format_time(all_entries[-1][1])}")
    return out_name


if __name__ == "__main__":
    print("=== Combining Japanese SRTs ===")
    combine("ja.whisperjav")
    print()
    print("=== Combining English SRTs ===")
    combine("ja.whisperjav.english")
