from pathlib import Path
import re

# ============================================================
# TARGET PROCESSED DOCUMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_DIR = BASE_DIR.parent / "schema"
INPUT_DIR = BASE_DIR.parent.parent / "eu_legislation" / "batch_00005" / "processed_docs"

FILE_PATH = INPUT_DIR / "JOL_2008_353_R_0001_01en.html"

FILE_PATH = Path("C:\\Users\\Roxas\\OneDrive\\Desktop\\Project_Space\\jurisynth\\kg_construction_pipeline\\intermediate\\batch_00005\\converted\\JOL_2008_353_R_0001_01en.md")

# ============================================================
# LOAD FILE
# ============================================================

text = FILE_PATH.read_text(
    encoding="utf-8",
    errors="replace",
)

file_size = FILE_PATH.stat().st_size

print("=" * 100)
print("DOCUMENT INSPECTION")
print("=" * 100)

print("Path       :", FILE_PATH)
print("File bytes :", f"{file_size:,}")
print("Characters :", f"{len(text):,}")
print("Lines      :", f"{text.count(chr(10)) + 1:,}")
print()

# ============================================================
# LONGEST LINES
# ============================================================

lines = text.splitlines()

line_stats = sorted(
    (
        (i + 1, len(line), line)
        for i, line in enumerate(lines)
    ),
    key=lambda x: x[1],
    reverse=True,
)

print("=" * 100)
print("LONGEST LINES")
print("=" * 100)

for rank, (line_no, length, line) in enumerate(
    line_stats[:20],
    start=1,
):
    print(
        f"{rank:02d}. "
        f"line={line_no:,} "
        f"chars={length:,}"
    )
    print(repr(line[:500]))
    print()

# ============================================================
# PARAGRAPH / BLOCK SIZES
# ============================================================

blocks = [
    block.strip()
    for block in re.split(r"\n\s*\n", text)
    if block.strip()
]

block_stats = sorted(
    (
        (i, len(block), block)
        for i, block in enumerate(blocks)
    ),
    key=lambda x: x[1],
    reverse=True,
)

print("=" * 100)
print("LARGEST PARAGRAPH / BLOCKS")
print("=" * 100)

for rank, (block_id, length, block) in enumerate(
    block_stats[:20],
    start=1,
):
    print(
        f"{rank:02d}. "
        f"block={block_id:,} "
        f"chars={length:,}"
    )
    print(repr(block[:500]))
    print()

# ============================================================
# ROUGH REPETITION CHECK
# ============================================================

normalized_lines = [
    re.sub(r"\s+", " ", line.strip())
    for line in lines
    if line.strip()
]

counts = {}

for line in normalized_lines:
    counts[line] = counts.get(line, 0) + 1

repeated = sorted(
    (
        (count, len(line), line)
        for line, count in counts.items()
        if count > 1
    ),
    key=lambda x: (
        x[0],
        x[1],
    ),
    reverse=True,
)

print("=" * 100)
print("MOST REPEATED NON-EMPTY LINES")
print("=" * 100)

for rank, (count, length, line) in enumerate(
    repeated[:20],
    start=1,
):
    print(
        f"{rank:02d}. "
        f"count={count:,} "
        f"chars={length:,}"
    )
    print(repr(line[:500]))
    print()

# ============================================================
# MARKDOWN TABLE-LIKE CONTENT
# ============================================================

table_like_lines = [
    line
    for line in lines
    if line.count("|") >= 2
]

print("=" * 100)
print("TABLE-LIKE CONTENT")
print("=" * 100)

print(
    "Lines with >= 2 pipe characters:",
    f"{len(table_like_lines):,}",
)

if table_like_lines:
    longest_table_lines = sorted(
        table_like_lines,
        key=len,
        reverse=True,
    )[:10]

    print()

    for rank, line in enumerate(
        longest_table_lines,
        start=1,
    ):
        print(
            f"{rank:02d}. chars={len(line):,}"
        )
        print(repr(line[:500]))
        print()