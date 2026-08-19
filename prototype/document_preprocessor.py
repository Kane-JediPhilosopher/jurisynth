from lxml import etree
from bs4 import BeautifulSoup
import faiss
import numpy as np
import os
import re
import json
from loky import get_reusable_executor
from sentence_transformers import SentenceTransformer
from pathlib import Path


HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]
LABEL_PATTERN = re.compile(r"(?i)\b(table|annex)\s+[\dIVXLCM]+")
BULLET_PATTERN = re.compile(r"^[-–—•▪]$")
NUMERIC_PATTERN = re.compile(r"\d")


# ---------- header/format detection helpers ----------

def numeric_ratio(cells):
    return sum(1 for c in cells if NUMERIC_PATTERN.search(c)) / len(cells) if cells else 0


def detect_header(all_rows):
    """Fallback header detection via numeric-density comparison (no <th>, no bold)."""
    if not all_rows:
        return None, list()
    
    if len(all_rows) >= 2:
        first_ratio = numeric_ratio(all_rows[0])
        rest_ratio = numeric_ratio([c for r in all_rows[1:] for c in r])

        if first_ratio < 0.2 and rest_ratio > 0.4:
            return all_rows[0], all_rows[1:]

    return None, all_rows


def linearize_row_preserving(rows):
    """Join cells within a row, keep rows as separate lines — never flatten by column."""

    return "\n".join(" — ".join(cell for cell in row if cell) for row in rows)


def classify_sparse(info):
    if info["cols"] == 2 and info["data"] and BULLET_PATTERN.match(info["data"][0][0].strip()):
        return "bullet_list"
    
    return "noise"


def reconstruct_list_text(info):
    return f"— {info['data'][0][1]}"


def classify_table_structure(table):
    """Reserved for later — everything currently routes to anchor_only by default."""
    if table["header"] and len(table["data"]) >= 3:
        return "triple_eligible"
    
    return "anchor_only"


def generate_anchor_sentence(table):
    if table["header"]:
        cols = ", ".join(table["header"])
        return f"Table {table['table_id']}, under {table['context']}, lists {cols}."
    
    return None


# ---------- single-pass triage ----------

def parse_html_safe(html_path):
    parser = etree.HTMLParser(huge_tree=True)
    tree = etree.parse(str(html_path), parser)
    html_bytes = etree.tostring(tree)
    del tree

    return BeautifulSoup(html_bytes, "lxml")

def triage_and_extract(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        soup = parse_html_safe(html_path)

    results = list()
    prev_cols = None
    context = None
    boundary_pending = False

    for tag in soup.find_all(True):
        if tag.name in HEADING_TAGS:
            text = tag.get_text(" ", strip=True)

            if text:
                context, boundary_pending = text, True

        elif tag.name == "p" and LABEL_PATTERN.search(tag.get_text(" ", strip=True)):
            context, boundary_pending = tag.get_text(" ", strip=True), True

        elif tag.name == "table" and tag.find_parent("table") is None:
            all_rows = list()

            for tr in tag.find_all("tr"):
                cells = list()

                for cell in tr.find_all(["td", "th"]):
                    span = int(cell.get("colspan", 1))
                    cells.extend([cell.get_text(" ", strip=True)] * span)

                all_rows.append(cells)

            has_explicit_th = tag.find("th") is not None
            first_row_cells = tag.find("tr").find_all(["td", "th"]) if tag.find("tr") else list()
            has_bold_row = bool(first_row_cells) and all(c.find(["b", "strong"]) for c in first_row_cells)

            if has_explicit_th or has_bold_row:
                header, rows_out = (all_rows[0], all_rows[1:]) if all_rows else (None, list())
            else:
                header, rows_out = detect_header(all_rows)

            cols = len(header) if header else (len(rows_out[0]) if rows_out else 0)

            if len(rows_out) + (1 if header else 0) <= 1:
                status = "sparse"
            elif header is None:
                status = "formatting"
            else:
                status = "candidate"

            possible_fragment = (
                        status == "candidate"
                and     prev_cols == cols
                and not boundary_pending
                and     header is None
            )

            results.append({
                "cols": cols,
                "rows": len(rows_out),
                "has_th": header is not None,
                "status": status,
                "possible_fragment_of_prev": possible_fragment,
                "context": context,
                "header": header,
                "data": rows_out,
                "tag": tag,
            })

            prev_cols, boundary_pending = cols, False

    return results, soup


# ---------- merge, replace, store ----------

def merge_fragments(results, doc_id):
    merged = list()
    current = None
    counter = 0

    for info in results:
        if info["status"] != "candidate":
            continue

        if info["possible_fragment_of_prev"] and current is not None:
            current["data"].extend(info["data"])
            current["tags"].append(info["tag"])
        else:
            if current is not None:
                merged.append(current)

            current = {
                "doc_id": doc_id,
                "table_id": counter,
                "header": info["header"],
                "data": info["data"],
                "context": info["context"],
                "tags": [info["tag"]]
            }

            counter += 1

    if current is not None:
        merged.append(current)

    return merged


def replace_tables_in_document(results, merged_tables):
    for info in results:
        if info["status"] == "sparse":
            kind = classify_sparse(info)

            if kind == "bullet_list":
                info["tag"].replace_with(reconstruct_list_text(info))
            else:
                info["tag"].decompose()

        elif info["status"] == "formatting":
            info["tag"].replace_with(linearize_row_preserving(info["data"]))

    for table in merged_tables:
        anchor = generate_anchor_sentence(table)
        table["tags"][0].replace_with(anchor or f"[table {table['table_id']} — description pending]")

        for extra_tag in table["tags"][1:]:
            extra_tag.decompose()


def store_table(table, storage_dir="table_store"):
    Path(storage_dir).mkdir(exist_ok=True)
    out = {"header": table["header"], "data": table["data"], "context": table["context"]}
    fname = f"{table['doc_id']}_{table['table_id']}.json"

    with open(f"{storage_dir}/{fname}", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False)


# ---------- Phase 1: per-document extraction (parallel) ----------

def extract_only(html_path, doc_id):
    results, soup = triage_and_extract(html_path)
    merged_tables = merge_fragments(results, doc_id)
    replace_tables_in_document(results, merged_tables)

    for table in merged_tables:
        store_table(table)
        del table["tags"]  # unpicklable bs4 refs — drop before crossing process boundary

    out_dir = Path("processed_docs")
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{doc_id}.html").write_text(str(soup), encoding="utf-8")

    return merged_tables


def run_batch_resilient(files, max_workers=None, min_workers=1):
    """Process files in parallel; on a crash, retry that chunk with fewer
    workers instead of losing the whole batch. Falls back to serial for
    files that still fail at 1 worker."""
    max_workers = max_workers or max(1, os.cpu_count() // 2)
    all_tables, failed = list(), list()

    def attempt(chunk, workers):
        executor = get_reusable_executor(max_workers=workers, timeout=60)
        try:
            futures = [executor.submit(extract_only, f, f.stem) for f in chunk]
            results = list()

            for fut in futures:
                results.extend(fut.result())

            return results, None

        except Exception as e:
            print(f"BROKE at {workers} workers: {e}")   # loky gives real errors now

            return None, chunk

    to_process = [(files, max_workers)]
    
    while to_process:
        chunk, workers = to_process.pop()
        results, broke = attempt(chunk, workers)

        if results is not None:
            all_tables.extend(results)
        elif workers > min_workers:
            print(f"Pool broke at {workers} workers on {len(chunk)} files — retrying at {workers // 2}")
            to_process.append((chunk, workers // 2))
        elif len(chunk) > 1:
            # still breaking at min_workers — split the chunk to isolate the bad file(s)
            mid = len(chunk) // 2
            to_process.append((chunk[:mid], min_workers))
            to_process.append((chunk[mid:], min_workers))
        else:
            print(f"CONFIRMED CRASH: {chunk[0]}")
            failed.append(chunk[0])

    return all_tables, failed


# ---------- Phase 2: one embedding pass over the whole batch ----------

def embed_and_index_tables(tables, embed_model, index, row_threshold=50, pool=None):
    texts = list()
    meta = list()

    for table in tables:
        if len(table["data"]) <= row_threshold:
            texts.append(f"{table['context']} | " + " | ".join(table["header"] or list()))
            meta.append({"doc_id": table["doc_id"], "table_id": table["table_id"], "type": "whole"})
        else:
            for row in table["data"]:
                texts.append(" | ".join(row))
                meta.append({"doc_id": table["doc_id"], "table_id": table["table_id"], "type": "row"})

    kwargs = {"batch_size": 128, "normalize_embeddings": True}

    if pool is not None:
        kwargs["pool"] = pool

    vectors = embed_model.encode(texts, **kwargs)
    index.add(np.array(vectors, dtype="float32"))

    return meta


emb_model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatIP(emb_model.get_embedding_dimension())

batch_files = list(Path("./big_samples").glob("*.html"))[:100]

all_tables = run_batch_resilient(batch_files)
print(f"Total tables collected: {len(all_tables)}")

pool = emb_model.start_multi_process_pool()
all_meta = embed_and_index_tables(all_tables, emb_model, index, pool=pool)
emb_model.stop_multi_process_pool(pool)

print(f"FAISS index size: {index.ntotal}")