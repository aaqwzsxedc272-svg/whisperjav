#!/usr/bin/env python3
"""Properly combine split SRT files with correct timestamp chaining."""

import re
from pathlib import Path

BASE = Path(".")
PARTS = [
    "HUNTA-010 - Lulustream.part01",
    "HUNTA-010 - Lulustream.part02",
    "HUNTA-010 - Lulustream.part03",
]

CREDIT_TEXTS = {
    "subs by whisperjav",
    "whisperjav 1.9.5 | balanced/aggressive",
}

CLOSING_CREDIT_START = 23 * 3600 + 59 * 60 + 58  # 23:59:58


def parse_time(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0


def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(path):
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
        body_lower = body.strip().lower()
        if body_lower in CREDIT_TEXTS:
            continue
        try:
            idx = int(lines[0].strip())
            if idx == 9999:
                continue
        except ValueError:
            pass
        if start >= CLOSING_CREDIT_START:
            continue
        entries.append((start, end, body))
    return entries


def combine(lang):
    offset = 0.0
    all_entries = []
    total_cues = 0

    for part in PARTS:
        path = BASE / f"{part}.{lang}.srt"
        if not path.exists():
            print(f"WARNING: {path} not found, skipping")
            continue
        entries = parse_srt(path)
        for start, end, body in entries:
            all_entries.append((start + offset, end + offset, body))
            total_cues += 1
        if entries:
            # FIX: offset chains from the offset-adjusted end time
            offset = all_entries[-1][1]
            print(f"  {part}: {len(entries)} cues, ends at {format_time(all_entries[-1][1])}")
        else:
            print(f"  {part}: 0 cues")

    out_name = f"HUNTA-010 - Lulustream.combined.{lang}.srt"
    with open(out_name, "w", encoding="utf-8") as f:
        for i, (start, end, body) in enumerate(all_entries, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time(start)} --> {format_time(end)}\n")
            f.write(f"{body}\n\n")

    print(f"\nWrote {out_name}: {total_cues} total cues")
    print(f"Total duration: {format_time(all_entries[-1][1])}")
    return all_entries


if __name__ == "__main__":
    print("=== Fixing Japanese combined SRT ===")
    ja_entries = combine("ja.whisperjav")
