#!/usr/bin/env python3
"""Extract Japanese cues from combined SRT into a JSON translation template."""

import json
import re
from pathlib import Path

text = Path("HUNTA-010 - Lulustream.combined.ja.whisperjav.srt").read_text(encoding="utf-8")
blocks = re.split(r"\n\s*\n", text.strip())

cues = []
cue_id = 0
for block in blocks:
    lines = block.strip().split("\n")
    if len(lines) < 3:
        continue
    m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", lines[1])
    if not m:
        continue
    cue_id += 1
    cues.append({
        "id": cue_id,
        "start": m.group(1),
        "end": m.group(2),
        "japanese": "\n".join(lines[2:]),
        "english": ""  # to be filled
    })

print(f"Total cues extracted: {len(cues)}")

# Save as JSON for batch translation
with open("japanese_cues.json", "w", encoding="utf-8") as f:
    json.dump(cues, f, ensure_ascii=False, indent=2)

# Show first 20 and last 20 cues
print("\n=== First 20 cues ===")
for c in cues[:20]:
    print(f"  [{c['id']}] {c['start']} --> {c['end']}: {c['japanese'][:80]}")

print("\n=== Last 20 cues ===")
for c in cues[-20:]:
    print(f"  [{c['id']}] {c['start']} --> {c['end']}: {c['japanese'][:80]}")

# Check which cues already have English (compare with existing English SRT)
print("\n=== Checking existing English coverage ===")
eng_text = Path("HUNTA-010 - Lulustream.combined.ja.whisperjav.english.srt").read_text(encoding="utf-8")
eng_blocks = re.split(r"\n\s*\n", eng_text.strip())
eng_cues = 0
for block in eng_blocks:
    lines = block.strip().split("\n")
    if len(lines) >= 3:
        m = re.match(r"([\d:,]+)\s*-->\s*([\d:,]+)", lines[1])
        if m:
            eng_cues += 1
print(f"English cues in existing file: {eng_cues}")
print(f"Missing English translations: {len(cues) - eng_cues}")
