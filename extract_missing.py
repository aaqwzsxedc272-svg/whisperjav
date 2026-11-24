#!/usr/bin/env python3
"""Extract Japanese cues that need English translation (part 01 cues 402+)."""

import json
import re
from pathlib import Path

# Load all Japanese cues
with open("japanese_cues.json", "r", encoding="utf-8") as f:
    all_cues = json.load(f)

# Part 01 is cues 1-1670, part 02 is 1671-3588, part 03 is 3589-3679
# English already covers cues 1-401 (part 01 first 22 min)
# Missing: cues 402-1670 (part 01 rest), plus verify parts 2-3

missing_p1 = [c for c in all_cues if 402 <= c["id"] <= 1670]
print(f"Part 01 missing cues: {len(missing_p1)}")

# Also check parts 2-3 for gaps
eng_text = Path("HUNTA-010 - Lulustream.combined.ja.whisperjav.english.srt").read_text(encoding="utf-8")
eng_blocks = re.split(r"\n\s*\n", eng_text.strip())
eng_cue_texts = []
for block in eng_blocks:
    lines = block.strip().split("\n")
    if len(lines) >= 3:
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", lines[1])
        if m:
            eng_cue_texts.append("\n".join(lines[2:]))

# For parts 2-3, compare by timestamp+japanese text
# But simpler: just save all missing cues
missing_all = [c for c in all_cues if c["id"] >= 402 and c["id"] <= 1670]

with open("p1_missing_cues.json", "w", encoding="utf-8") as f:
    json.dump(missing_all, f, ensure_ascii=False, indent=2)

print(f"Saved {len(missing_all)} part 01 missing cues to p1_missing_cues.json")

# Show first 20
print("\n=== First 20 missing cues (part 01) ===")
for c in missing_all[:20]:
    print(f"  [{c['id']}] {c['start']} --> {c['end']}: {c['japanese'][:70]}")

# Show around the transition area
print("\n=== Around cue 400-410 ===")
for c in missing_all:
    if 400 <= c["id"] <= 410:
        print(f"  [{c['id']}] {c['start']} --> {c['end']}: {c['japanese'][:70]}")
