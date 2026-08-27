from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import re
import gc
import os
import psutil
import shutil

import faiss
import numpy as np
from lxml import html

# =============================================================================
# Configuration
# =============================================================================

HEADING_TAGS = ["h1", "h2", "h3", "h4", "h5", "h6"]

LABEL_PATTERN = re.compile(
    r"(?i)\b(table|annex|appendix)\s+[\dIVXLCM]+"
)

COLUMN_NUMBER_PATTERN = re.compile(
    r"^\(?\s*\d+\s*\)?$"
)

NUMERIC_PATTERN = re.compile(r"\d")

BULLET_PATTERN = re.compile(
    r"^[-–—•▪]$"
)

DEFAULT_TABLE_STORE = "table_store"
DEFAULT_PROCESSED_DIR = "processed_docs"

MAX_HEADER_ROWS = 3


# =============================================================================
# Helper functions
# =============================================================================

def memory_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024**2


def has_parent_table(tag):
    parent = tag.getparent()

    while parent is not None:
        if parent.tag == "table":
            return True
        parent = parent.getparent()

    return False


def replace_element_with_text(element, text):
    """
    Replace an lxml element with a span containing plain text.
    """

    parent = element.getparent()

    if parent is None:
        return

    replacement = html.Element("span")
    replacement.text = text

    parent.replace(
        element,
        replacement,
    )


def remove_element(element):
    """Remove an lxml element from its parent."""

    parent = element.getparent()

    if parent is not None:
        parent.remove(element)


def normalize_table_rows(rows):
    """
    Normalize table rows while preserving cell positions.

    Completely empty rows are discarded.
    """

    normalized = []

    for row in rows:

        cells = [
            str(cell).strip()
            for cell in row
        ]

        if any(cells):
            normalized.append(cells)

    return normalized


def row_width(row):
    """Return the number of cells in a row."""

    return len(row or [])


def consistent_row_width(rows):
    """Return True when all non-empty rows have the same width."""

    widths = [
        row_width(row)
        for row in rows
        if row
    ]

    return (
        bool(widths)
        and len(set(widths)) == 1
    )


def numeric_ratio(cells):
    """
    Proportion of non-empty cells containing at least one digit.
    """

    cells = [
        str(cell).strip()
        for cell in cells
        if str(cell).strip()
    ]

    if not cells:
        return 0.0

    return sum(
        bool(NUMERIC_PATTERN.search(cell))
        for cell in cells
    ) / len(cells)


def is_column_number_row(row):
    """
    Detect structural column-number rows such as:

        (1) | (2)
        (1) | (2) | (3) | (4)
    """

    if not row:
        return False

    cells = [
        str(cell).strip()
        for cell in row
        if str(cell).strip()
    ]

    if not cells:
        return False

    return all(
        COLUMN_NUMBER_PATTERN.fullmatch(cell)
        for cell in cells
    )


def normalize_cell_text(value):
    """Normalize cell text for conservative comparison."""

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower(),
    )


def rows_are_similar(row_a, row_b):
    """Conservatively compare two rows."""

    if not row_a or not row_b:
        return False

    if len(row_a) != len(row_b):
        return False

    return all(
        normalize_cell_text(a)
        == normalize_cell_text(b)
        for a, b in zip(row_a, row_b)
    )


# =============================================================================
# Table structure extraction
# =============================================================================

def extract_header_rows(table):
    """
    Extract explicit HTML header rows while preserving multi-row
    header structure.

    Supports:
        - <thead>
        - <th>
        - colspan
        - rowspan

    Returns:
        A list of logical header rows.

    Example HTML structure:

        <tr>
            <th rowspan="2">Country</th>
            <th colspan="2">Area of applicability</th>
        </tr>
        <tr>
            <th>Code</th>
            <th>Value</th>
        </tr>

    becomes:

        [
            ["Country", "Area of applicability", "Area of applicability"],
            ["Country", "Code", "Value"],
        ]

    The repeated rowspan value is intentional. It is removed later
    when the hierarchical header is flattened.
    """

    # -----------------------------------------------------------------
    # Identify physical header rows.
    # -----------------------------------------------------------------

    header_rows = table.xpath(
        "./thead/tr"
    )

    # If no <thead> exists, look for direct/early rows containing <th>.
    if not header_rows:

        candidate_rows = table.xpath(
            "./tr | ./tbody/tr | ./tfoot/tr"
        )

        header_rows = []

        for tr in candidate_rows:

            cells = tr.xpath(
                "./th | ./td"
            )

            if not cells:
                continue

            has_th = bool(
                tr.xpath("./th")
            )

            if not has_th:
                # Stop once the actual data section begins.
                if header_rows:
                    break

                continue

            header_rows.append(tr)

    if not header_rows:
        return []

    # -----------------------------------------------------------------
    # Build a logical grid while respecting rowspan/colspan.
    # -----------------------------------------------------------------

    grid = []

    # Tracks cells occupied by rowspans from previous rows.
    occupied = {}

    for row_index, tr in enumerate(header_rows):

        row = []
        column = 0

        cells = tr.xpath(
            "./th | ./td"
        )

        for cell in cells:

            # ---------------------------------------------------------
            # Find the next free logical column.
            # ---------------------------------------------------------

            while (
                (row_index, column)
                in occupied
            ):
                column += 1

            # ---------------------------------------------------------
            # Cell text.
            # ---------------------------------------------------------

            text = " ".join(
                "".join(
                    cell.itertext()
                ).split()
            )

            # ---------------------------------------------------------
            # rowspan / colspan.
            # ---------------------------------------------------------

            try:
                rowspan = int(
                    cell.get("rowspan", "1")
                )
            except (
                TypeError,
                ValueError,
            ):
                rowspan = 1

            try:
                colspan = int(
                    cell.get("colspan", "1")
                )
            except (
                TypeError,
                ValueError,
            ):
                colspan = 1

            rowspan = max(rowspan, 1)
            colspan = max(colspan, 1)

            # ---------------------------------------------------------
            # Ensure current row is wide enough.
            # ---------------------------------------------------------

            required_width = (
                column + colspan
            )

            if len(row) < required_width:
                row.extend(
                    [""] * (
                        required_width
                        - len(row)
                    )
                )

            # ---------------------------------------------------------
            # Place the cell across its colspan.
            # ---------------------------------------------------------

            for offset in range(colspan):

                target_column = (
                    column + offset
                )

                row[target_column] = text

                # -----------------------------------------------------
                # Record rowspan occupancy.
                # -----------------------------------------------------

                if rowspan > 1:

                    for future_offset in range(
                        1,
                        rowspan,
                    ):
                        occupied[
                            (
                                row_index
                                + future_offset,
                                target_column,
                            )
                        ] = True

            column += colspan

        grid.append(row)

    return grid


def flatten_header_rows(header_rows):
    """
    Flatten a multi-row hierarchical header into one semantic header.

    Parent and child labels are concatenated using:

        "Parent | Child"

    Repeated labels caused by rowspan are collapsed.

    Example:

        [
            ["Country", "Area of applicability", "Area of applicability"],
            ["Country", "Code", "Value"],
        ]

    becomes:

        [
            "Country",
            "Area of applicability | Code",
            "Area of applicability | Value",
        ]

    Empty cells are ignored.

    This function performs no semantic inference. It only reflects
    the structural relationships already encoded by the HTML table.
    """

    if not header_rows:
        return None

    # -----------------------------------------------------------------
    # Determine logical width.
    # -----------------------------------------------------------------

    width = max(
        (
            len(row)
            for row in header_rows
            if row
        ),
        default=0,
    )

    if width == 0:
        return None

    flattened = []

    for column_index in range(width):

        parts = []

        for row in header_rows:

            if column_index >= len(row):
                continue

            value = str(
                row[column_index]
            ).strip()

            if not value:
                continue

            # ---------------------------------------------------------
            # Avoid duplicates caused by rowspan.
            #
            # Also avoids:
            #
            #   "Code | Code"
            #
            # when malformed HTML happens to repeat a label.
            # ---------------------------------------------------------

            if any(
                normalize_cell_text(
                    value
                )
                == normalize_cell_text(
                    existing
                )
                for existing in parts
            ):
                continue

            parts.append(value)

        flattened.append(
            " | ".join(parts)
        )

    return flattened


def extract_direct_rows(table):
    """
    Extract rows belonging directly to this table.

    Nested tables are not flattened into the parent table.

    colspan is respected by repeating the cell value across the
    corresponding number of logical columns.
    """

    rows = []

    for tr in table.xpath("./tr | ./tbody/tr | ./thead/tr | ./tfoot/tr"):

        cells = tr.xpath("./td | ./th")

        if not cells:
            continue

        logical_cells = []

        for cell in cells:

            try:
                colspan = int(
                    cell.get("colspan", "1")
                )
            except (TypeError, ValueError):
                colspan = 1

            text = " ".join(
                "".join(
                    cell.itertext()
                ).split()
            )

            logical_cells.extend(
                [text] * max(colspan, 1)
            )

        if logical_cells:
            rows.append(logical_cells)

    return rows


def has_nested_table(table):
    """Return True if this table contains another table."""

    return bool(table.xpath(".//table"))


def has_explicit_header(table):
    """
    Detect explicit HTML header semantics.

    <thead> or direct <th> usage is considered explicit.
    """

    if table.xpath("./thead"):
        return True

    return bool(
        table.xpath(
            "./tr/th | ./tbody/tr/th | ./tfoot/tr/th"
        )
    )


def first_row_is_bold(table):
    """
    Detect a first row whose direct cells are all bold/strong.

    Kept as a weak formatting signal rather than a primary header
    detector. It is intentionally not sufficient by itself to
    classify a table as semantic.
    """

    first_rows = table.xpath(
        "./tr | ./tbody/tr | ./thead/tr | ./tfoot/tr"
    )

    if not first_rows:
        return False

    first_tr = first_rows[0]

    cells = first_tr.xpath(
        "./td | ./th"
    )

    return (
        bool(cells)
        and all(
            cell.xpath(
                "./b | ./strong"
            )
            for cell in cells
        )
    )


def textual_ratio(cells):
    """
    Return the proportion of non-empty cells that contain letters.

    Unlike numeric_ratio(), this also works for multilingual text.
    """
    cells = [
        str(cell).strip()
        for cell in cells
        if str(cell).strip()
    ]

    if not cells:
        return 0.0

    return sum(
        1
        for cell in cells
        if re.search(r"[^\W\d_]", cell, flags=re.UNICODE)
    ) / len(cells)


def row_text_density(row):
    """
    Measure how much textual content exists in a row.

    Used for detecting textual/multilingual headers.
    """
    cells = [
        str(cell).strip()
        for cell in row
        if str(cell).strip()
    ]

    if not cells:
        return 0.0

    return sum(
        bool(
            re.search(
                r"[^\W\d_]",
                cell,
                flags=re.UNICODE,
            )
        )
        for cell in cells
    ) / len(cells)


def looks_like_textual_header(header, data_rows):
    """
    Detect headers in tables where both the header and data are
    predominantly textual.

    Examples:
        In Greek | In English
        Λεμεσός   | Lemesos

        Value | Meaning (EN) | Meaning (BG)
        INF   | Information  | Информация

    This is intentionally conservative.
    """

    if not header or not data_rows:
        return False

    header_width = len(header)

    if header_width < 2:
        return False

    # Require several rows when possible so that an isolated
    # two-row structure is not automatically treated as a table.
    comparable_rows = [
        row
        for row in data_rows[:5]
        if len(row) == header_width
    ]

    if not comparable_rows:
        return False

    # Header should be strongly textual.
    if row_text_density(header) < 0.5:
        return False

    # Examine the first few data rows.
    data_text_density = sum(
        row_text_density(row)
        for row in comparable_rows
    ) / len(comparable_rows)

    if data_text_density < 0.5:
        return False

    # A header normally contains column-label-like phrases,
    # whereas data rows tend to contain shorter record values.
    header_lengths = [
        len(str(cell).strip())
        for cell in header
        if str(cell).strip()
    ]

    data_lengths = [
        len(str(cell).strip())
        for row in comparable_rows
        for cell in row
        if str(cell).strip()
    ]

    if not header_lengths or not data_lengths:
        return False

    avg_header_length = (
        sum(header_lengths)
        / len(header_lengths)
    )

    avg_data_length = (
        sum(data_lengths)
        / len(data_lengths)
    )

    # Headers tend to be at least reasonably descriptive.
    if avg_header_length < 3:
        return False

    # Require at least two populated records.
    if len(comparable_rows) < 2:
        return False

    # Strongest signal: header is at least as descriptive as the
    # average data cell, or contains obvious label vocabulary.
    label_signal = any(
        re.search(
            r"(?i)\b("
            r"code|value|name|description|meaning|"
            r"type|category|unit|date|country|"
            r"english|greek|french|german|"
            r"element|identifier|id"
            r")\b",
            str(cell),
        )
        for cell in header
    )

    return (
        avg_header_length >= avg_data_length * 0.6
        or label_signal
    )


# =============================================================================
# Header detection
# =============================================================================

def detect_header(all_rows):
    """
    Infer a semantic header from the beginning of a table.

    Returns:
        (header, data_rows)

    The function is deliberately conservative:
    failure to infer a header does NOT imply that the table
    is non-semantic.

    Supported patterns include:

        Header
        ------
        data
        data

    and:

        Header
        (1) | (2)
        data
        data

    and simple multi-row headers.
    """

    if not all_rows:
        return None, []

    rows = normalize_table_rows(all_rows)

    if not rows:
        return None, []

    # -----------------------------------------------------------------
    # Remove column-number metadata immediately following a plausible
    # header candidate.
    # -----------------------------------------------------------------

    if len(rows) >= 2:

        first = rows[0]

        if (
            not is_column_number_row(first)
            and is_column_number_row(rows[1])
        ):

            first_ratio = numeric_ratio(first)

            if first_ratio < 0.5:
                return (
                    first,
                    rows[2:],
                )

    # -----------------------------------------------------------------
    # Simple one-row header.
    #
    # A likely header is relatively textual while the following
    # rows contain more numeric material.
    # -----------------------------------------------------------------

    if len(rows) >= 2:

        first = rows[0]

        remaining = [
            cell
            for row in rows[1:]
            for cell in row
        ]

        first_ratio = numeric_ratio(first)
        rest_ratio = numeric_ratio(remaining)

        if (
            first_ratio < 0.35
            and rest_ratio > 0.30
            and len(first) == len(rows[1])
        ):
            return (
                first,
                rows[1:],
            )


    # -----------------------------------------------------------------
    # Textual / multilingual header.
    #
    # A textual header is inherently ambiguous in headerless legal
    # tables. Treat this signal as insufficient on its own; explicit
    # headers and stronger structural signals above take precedence.
    # -----------------------------------------------------------------

    # -----------------------------------------------------------------
    # No reliable header found.
    #
    # IMPORTANT:
    # The table can still be semantic.
    # -----------------------------------------------------------------

    return None, rows


# =============================================================================
# Semantic-table detection
# =============================================================================

def looks_like_semantic_table(
    rows,
    header=None,
):
    """
    Determine whether a table contains meaningful structured content.

    This deliberately does NOT require:

        <thead>
        <th>
        bold formatting
        CSS classes
        an inferred header

    Headerless semantic tables are therefore valid.

    The detector is primarily a noise filter for layout/formatting
    tables, not a semantic classifier.
    """

    if not rows:
        return False
        

    data_rows = normalize_table_rows(rows)

    if not data_rows:
        return False

    # -------------------------------------------------------------------------
    # Minimum structural size
    # -------------------------------------------------------------------------

    effective_rows = list(data_rows)

    if header:
        effective_rows.insert(
            0,
            header,
        )

    if len(effective_rows) < 2:
        return False

    # -------------------------------------------------------------------------
    # Need at least two logical columns.
    # -------------------------------------------------------------------------

    max_cols = max(
        len(row)
        for row in effective_rows
        if row
    )

    if max_cols < 2:
        return False

    # -------------------------------------------------------------------------
    # Need enough meaningful cell content.
    # -------------------------------------------------------------------------

    all_cells = [
        str(cell).strip()
        for row in effective_rows
        for cell in row
        if str(cell).strip()
    ]

    if len(all_cells) < 4:
        return False

    meaningful_cells = sum(
        bool(
            re.search(
                r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]",
                cell,
            )
        )
        for cell in all_cells
    )

    if meaningful_cells < 4:
        return False

    # -------------------------------------------------------------------------
    # Reject obvious repeated single-marker tables.
    #
    # This helps remove some layout artifacts while preserving real
    # headerless tables.
    # -------------------------------------------------------------------------

    if all(
        len(row) == 1
        for row in effective_rows
    ):
        return False

    # -------------------------------------------------------------------------
    # Reject tables where every cell is effectively the same marker.
    # -------------------------------------------------------------------------

    normalized_cells = [
        normalize_cell_text(cell)
        for cell in all_cells
    ]

    if (
        normalized_cells
        and len(set(normalized_cells)) == 1
    ):
        return False

    # -------------------------------------------------------------------------
    # Otherwise retain the table.
    #
    # We intentionally do not demand numeric content. Legal tables can
    # be entirely textual.
    # -------------------------------------------------------------------------

    return True


# =============================================================================
# Sparse / formatting handling
# =============================================================================

def linearize_table_tree(table):
    """
    Recursively flatten a table and its nested tables into readable text.

    Each direct row is represented as:
        cell 1 — cell 2 — ...

    Nested tables are recursively appended in document order.
    """
    lines = []

    for tr in table.xpath("./tr | ./tbody/tr | ./thead/tr | ./tfoot/tr"):
        cells = tr.xpath("./td | ./th")

        if not cells:
            continue

        direct_parts = []

        for cell in cells:
            # Extract only text belonging directly to this cell,
            # excluding nested tables.
            nested_tables = cell.xpath(".//table")

            if nested_tables:
                # Clone-like extraction: collect text from descendants
                # while excluding nested table subtrees.
                parts = []

                for node in cell.iter():
                    if node is cell:
                        continue

                    if node.tag == "table":
                        continue

                    if node.getparent() is not None:
                        ancestor_table = node.getparent()
                        while ancestor_table is not None and ancestor_table is not cell:
                            if ancestor_table.tag == "table":
                                break
                            ancestor_table = ancestor_table.getparent()

                        if ancestor_table is not None and ancestor_table.tag == "table":
                            continue

                    if node.tag in {"p", "span"} and node.text:
                        parts.append(node.text.strip())

                text = " ".join(parts)
            else:
                text = " ".join("".join(cell.itertext()).split())

            if text:
                direct_parts.append(text)

        if direct_parts:
            lines.append(" — ".join(direct_parts))

        # Now recursively append nested tables.
        for nested in tr.xpath(".//table"):
            lines.extend(linearize_table_tree(nested))

    return lines


def classify_sparse(info):
    """
    Classify very small table fragments.
    """

    data = info.get("data") or []

    if (
        info.get("cols") == 2
        and data
        and data[0]
        and BULLET_PATTERN.fullmatch(
            data[0][0].strip()
        )
    ):
        return "bullet_list"

    return "noise"


def looks_like_layout_container(table, rows):
    """
    Detect tables that primarily provide HTML layout/indentation around
    nested prose or list-like content.

    Nested tables alone are not sufficient evidence.
    """
    if not has_nested_table(table):
        return False

    if not rows:
        return False

    # Layout containers commonly have very few direct rows and columns,
    # while most of their actual content lives in nested tables.
    direct_cells = [
        str(cell).strip()
        for row in rows
        for cell in row
        if str(cell).strip()
    ]

    if not direct_cells:
        return False

    # A nested container with a small direct surface is more likely
    # to be structural than a genuine table containing its own data.
    max_cols = max(len(row) for row in rows if row)

    if max_cols > 3:
        return False

    # If the table has nested tables and its direct content consists
    # primarily of prose/labels rather than multiple independent records,
    # treat it as a layout container.
    nested_count = len(table.xpath(".//table"))
    direct_count = len(direct_cells)

    return nested_count >= direct_count


def reconstruct_list_text(info):
    """Convert a two-column bullet table into plain text."""

    data = info.get("data") or []

    if not data or len(data[0]) < 2:
        return ""

    return f"— {data[0][1]}"


def linearize_rows(rows):
    """
    Convert rows to readable plain text.

    Used only for tables explicitly classified as formatting/layout.
    """

    return "\n".join(
        " — ".join(
            str(cell).strip()
            for cell in row
            if str(cell).strip()
        )
        for row in rows
        if row
    )


# =============================================================================
# Phase 1: HTML triage
# =============================================================================

def triage_and_extract(html_path):
    """
    Parse one HTML document and classify top-level tables.

    Returns:

        results, soup

    Each result contains enough information for fragment merging,
    replacement, diagnostics, and later JSON persistence.
    """

    html_path = Path(html_path)

    document = html.parse(
        str(html_path),
    )
    root = document.getroot()

    results = []

    previous = None
    context = None
    boundary_pending = False

    for tag in root.iter():

        # =====================================================================
        # Document context
        # =====================================================================

        if tag.tag in HEADING_TAGS:
            text = " ".join(tag.itertext()).strip()

            if text:
                context = text
                boundary_pending = True

            continue

        if tag.tag == "p":
            text = " ".join(tag.itertext()).strip()

            if LABEL_PATTERN.search(text):
                context = text
                boundary_pending = True

            continue

        # =====================================================================
        # Tables
        # =====================================================================

        if tag.tag != "table":
            continue

        # Only inspect top-level tables.
        if has_parent_table(tag):
            continue

        all_rows = extract_direct_rows(tag)

        if not all_rows:
            continue

        nested = has_nested_table(tag)

        layout_container = looks_like_layout_container(
            tag,
            all_rows,
        )

        explicit_th = has_explicit_header(tag)
        bold_first = first_row_is_bold(tag)

        # ---------------------------------------------------------------------
        # Fragment detection
        #
        # Determine whether this table is a continuation BEFORE header
        # inference, so the first row of a continuation cannot be mistaken
        # for a new header.
        # ---------------------------------------------------------------------

        current_width = len(all_rows[0])

        possible_fragment = (
            previous is not None
            and previous["status"] == "candidate"
            and previous["cols"] == current_width
            and not boundary_pending
            and not explicit_th
            and not nested
            and not previous["nested"]
        )

        # ---------------------------------------------------------------------
        # Header handling
        # ---------------------------------------------------------------------

        if possible_fragment:
            header = None
            data_rows = all_rows
            header_source = None

        elif explicit_th:
            header_rows = extract_header_rows(tag)

            if header_rows:
                header = flatten_header_rows(header_rows)

                header_row_count = len(header_rows)

                data_rows = all_rows[header_row_count:]

                header_source = "explicit"

            else:
                header = all_rows[0]
                data_rows = all_rows[1:]
                header_source = "explicit"

        else:
            header, data_rows = detect_header(all_rows)

            if header is not None:
                header_source = "inferred"
            else:
                header_source = None


        # ---------------------------------------------------------------------
        # Semantic filtering
        # ---------------------------------------------------------------------

        semantic = looks_like_semantic_table(
            data_rows,
            header=header,
        )

        if layout_container:
            status = "layout"
        elif not semantic:
            status = "sparse"
        else:
            status = "candidate"

        cols = (
            len(header)
            if header
            else (
                len(data_rows[0])
                if data_rows
                else 0
            )
        )

        total_rows = (
            len(data_rows)
            + (1 if header else 0)
        )

        # ---------------------------------------------------------------------
        # Fragment detection
        #
        # A continuation should:
        #
        #   - be semantic
        #   - not have an explicit HTML header
        #   - have the same width as the previous candidate
        #   - not be separated by a heading/table label
        #   - not be nested
        #
        # Inferred headers are allowed here because a fragment may begin with
        # ordinary <td> cells that the header heuristic mistakes for a header.
        # ---------------------------------------------------------------------

        current_width = cols

        possible_fragment = False

        if (
            status == "candidate"
            and previous is not None
            and previous["status"] == "candidate"
            and previous["cols"] == current_width
            and not boundary_pending
            and not explicit_th
            and not nested
            and not previous["nested"]
        ):
            possible_fragment = True

        info = {
            "tag": tag,
            "data": data_rows,
            "header": header,
            "header_source": header_source,
            "has_explicit_th": explicit_th,
            "bold_first": bold_first,
            "has_header": header is not None,
            "cols": cols,
            "rows": total_rows,
            "nested": nested,
            "status": status,
            "possible_fragment_of_prev":
                possible_fragment,
            "context": context,
            "layout_container": layout_container,
        }

        results.append(info)

        previous = info
        boundary_pending = False

    return results, document


# =============================================================================
# Phase 1b: Fragment merging
# =============================================================================

def merge_fragments(results, doc_id):
    """
    Merge genuinely continuous semantic table fragments.

    Headerless fragments are allowed to merge.

    We deliberately do NOT merge across:
        - headings
        - table/annex labels
        - inferred headers
        - explicit headers
        - nested tables

    The goal is to prevent unrelated neighbouring tables from being
    silently concatenated.
    """

    merged = []
    current = None
    counter = 0

    for info in results:

        if info["status"] != "candidate":
            continue

        # ---------------------------------------------------------------------
        # Existing table + continuation fragment
        # ---------------------------------------------------------------------

        if (
            current is not None
            and info["possible_fragment_of_prev"]
            and not info["has_explicit_th"]
        ):
            current["data"].extend(info["data"])
            current["tags"].append(info["tag"])

            continue

        # ---------------------------------------------------------------------
        # Start a new semantic table
        # ---------------------------------------------------------------------

        if current is not None:
            merged.append(current)

        current = {
            "doc_id": doc_id,
            "table_id": counter,
            "header": info["header"],
            "data": list(info["data"]),
            "context": info["context"],
            "tags": [info["tag"]],
            "header_source": info[
                "header_source"
            ],
        }

        counter += 1

    if current is not None:
        merged.append(current)

    return merged


# =============================================================================
# Phase 1c: Document replacement
# =============================================================================

def replace_tables_in_document(results, merged_tables):
    """
    Remove formatting/layout tables from the processed HTML.

    Semantic tables are preserved only in the JSON table store.
    Layout containers are recursively linearized into plain text.
    """

    # ---------------------------------------------------------------------
    # Layout containers
    # ---------------------------------------------------------------------

    for info in results:
        if info.get("status") != "layout":
            continue

        text = "\n".join(
            linearize_table_tree(info["tag"])
        ).strip()

        if text:
            replace_element_with_text(
                info["tag"],
                text,
            )
        else:
            remove_element(info["tag"])

    # ---------------------------------------------------------------------
    # Sparse / formatting tables
    # ---------------------------------------------------------------------

    for info in results:
        if info["status"] != "sparse":
            continue

        kind = classify_sparse(info)

        if kind == "bullet_list":
            text = reconstruct_list_text(info)

            if text:
                replace_element_with_text(
                    info["tag"],
                    text,
                )
            else:
                remove_element(info["tag"])
        else:
            remove_element(info["tag"])

    # ---------------------------------------------------------------------
    # Semantic tables
    #
    # Do nothing.
    # Their structured contents are persisted separately.
    # ---------------------------------------------------------------------


# =============================================================================
# Phase 1d: JSON persistence
# =============================================================================

def store_table(
    table,
    storage_dir=DEFAULT_TABLE_STORE,
):
    """
    Persist a semantic table.

    JSON is the source of truth for exact table reconstruction.
    Only table-level provenance metadata is stored alongside it.
    """

    storage_path = Path(storage_dir)
    storage_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output = {
        "doc_id": table["doc_id"],
        "table_id": table["table_id"],
        "context": table.get("context"),
        "header": table.get("header"),
        "data": table.get("data") or [],
    }

    path = (
        storage_path
        / (
            f"{table['doc_id']}_"
            f"{table['table_id']}.json"
        )
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return path


# =============================================================================
# Phase 1e: Per-document worker
# =============================================================================

def extract_only(
    html_path,
    doc_id,
    table_store=DEFAULT_TABLE_STORE,
    processed_dir=DEFAULT_PROCESSED_DIR,
):
    """
    Run the complete HTML/table extraction phase for one document.

    No FAISS, NumPy, or embedding state is created here.
    """

    results, document = triage_and_extract(
        html_path
    )

    merged_tables = merge_fragments(
        results,
        doc_id,
    )

    replace_tables_in_document(
        results,
        merged_tables,
    )

    # -------------------------------------------------------------------------
    # Diagnostics
    # -------------------------------------------------------------------------

    source_tables = len(results)

    sparse_tables = sum(
        info["status"] == "sparse"
        for info in results
    )

    candidate_tables = sum(
        info["status"] == "candidate"
        for info in results
    )

    explicit_header_tables = sum(
        info["has_explicit_th"]
        for info in results
        if info["status"] == "candidate"
    )

    inferred_header_tables = sum(
        (
            info["header_source"] == "inferred"
            and info["status"] == "candidate"
        )
        for info in results
    )

    headerless_candidate_tables = sum(
        (
            not info["has_header"]
            and info["status"] == "candidate"
        )
        for info in results
    )

    nested_candidate_tables = sum(
        (
            info["nested"]
            and info["status"] == "candidate"
        )
        for info in results
    )

    semantic_tables = len(
        merged_tables
    )

    semantic_rows = sum(
        len(table.get("data") or [])
        for table in merged_tables
    )

    merged_fragments = sum(
        max(
            len(table.get("tags") or []) - 1,
            0,
        )
        for table in merged_tables
    )

    merged_semantic_tables = sum(
        len(table.get("tags") or []) > 1
        for table in merged_tables
    )

    headerless_semantic_tables = sum(
        not table.get("header")
        for table in merged_tables
    )

    # -------------------------------------------------------------------------
    # Persist semantic tables
    # -------------------------------------------------------------------------

    for table in merged_tables:

        store_table(
            table,
            table_store,
        )

        # Remove lxml DOM nodes before returning from the worker.
        del table["tags"]

    # -------------------------------------------------------------------------
    # Persist processed HTML
    # -------------------------------------------------------------------------

    output_dir = Path(
        processed_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{doc_id}.html"
    )

    output_path.write_text(
        html.tostring(
            document.getroot(),
            encoding="unicode",
            method="html",
        ),
        encoding="utf-8",
    )

    del document
    del results

    gc.collect()
    

    # -------------------------------------------------------------------------
    # Return picklable data only
    # -------------------------------------------------------------------------

    return {
        "doc_id": doc_id,
        "processed_path": str(
            output_path
        ),
        "tables": merged_tables,
        "diagnostics": {
            "source_tables": source_tables,
            "sparse_tables": sparse_tables,
            "candidate_tables": candidate_tables,
            "explicit_header_tables":
                explicit_header_tables,
            "inferred_header_tables":
                inferred_header_tables,
            "headerless_candidate_tables":
                headerless_candidate_tables,
            "nested_candidate_tables":
                nested_candidate_tables,
            "semantic_tables":
                semantic_tables,
            "semantic_rows":
                semantic_rows,
            "merged_fragments":
                merged_fragments,
            "merged_semantic_tables":
                merged_semantic_tables,
            "headerless_semantic_tables":
                headerless_semantic_tables,
        },
    }


# =============================================================================
# Phase 1f: Parallel extraction
# =============================================================================

def run_batch(
    batch_files,
    max_workers=2,
    table_store=DEFAULT_TABLE_STORE,
    processed_dir=DEFAULT_PROCESSED_DIR,
):
    """
    Execute extraction in parallel.

    Successful documents return their extraction result.
    Failed documents return a lightweight failure record.
    """

    batch_files = [Path(path) for path in batch_files]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                extract_only,
                path,
                path.stem,
                table_store,
                processed_dir,
            ): path
            for path in batch_files
        }

        for future in as_completed(futures):
            source_path = futures[future]

            try:
                result = future.result()
            except Exception as exc:
                yield {
                    "doc_id": source_path.stem,
                    "status": "failed",
                    "error": str(exc),
                }
            else:
                result["status"] = "success"
                yield result


# =============================================================================
# Phase 2: Table-level retrieval text
# =============================================================================

def build_table_retrieval_text(table):
    parts = []

    if table.get("context"):
        parts.append(str(table["context"]).strip())

    if table.get("header"):
        parts.append(
            " | ".join(
                str(column).strip()
                for column in table["header"]
                if str(column).strip()
            )
        )

    return " — ".join(parts).strip()


def build_table_retrieval_units(
    tables,
):
    """
    Build table-level retrieval units.

    One vector is created per semantic table.
    """

    texts = []
    metadata = []

    for table in tables:

        text = build_table_retrieval_text(
            table
        )

        if not text:
            continue

        texts.append(text)

        metadata.append({
            "doc_id": table["doc_id"],
            "table_id": table["table_id"],
            "type": "table",
        })

    return texts, metadata


# =============================================================================
# Phase 2b: Row retrieval text
# =============================================================================

def build_row_retrieval_text(row):
    """
    Build a row-only embedding representation.

    Headers and table descriptions are intentionally excluded because
    the table-level index already represents table identity.
    """

    return " | ".join(
        str(cell).strip()
        for cell in row
        if str(cell).strip()
    )


def build_row_retrieval_units(
    tables,
):
    """
    Group row retrieval units by table.
    """

    units = {}

    for table in tables:

        table_key = (
            table["doc_id"],
            table["table_id"],
        )

        rows = table.get("data") or []

        units[table_key] = {
            "rows": [],
            "metadata": [],
        }

        for row_id, row in enumerate(rows):

            text = build_row_retrieval_text(
                row
            )

            if not text:
                continue

            units[table_key]["rows"].append(
                text
            )

            units[table_key]["metadata"].append({
                "doc_id": table["doc_id"],
                "table_id": table["table_id"],
                "row_id": row_id,
                "type": "row",
            })

    return units


# =============================================================================
# Phase 2c: Hierarchical indexing
# =============================================================================

def build_table_index(
    tables,
    embed_model,
    batch_size=128,
):
    """
    Build the hierarchical table/row retrieval structure.

        Query
          ↓
        table-level FAISS
          ↓
        candidate tables
          ↓
        row-level FAISS within candidate tables
          ↓
        final row hits

    All row embeddings are produced in one batched embedding pass.
    """

    # =========================================================================
    # Pass 1: table embeddings
    # =========================================================================

    table_texts, table_metadata = (
        build_table_retrieval_units(
            tables
        )
    )

    if not table_texts:
        return {
            "table_index": None,
            "table_metadata": [],
            "row_indices": {},
            "row_metadata": {},
        }

    print(
        f"Table-level units: "
        f"{len(table_texts):,}"
    )

    table_vectors = embed_model.encode(
        table_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    table_vectors = np.asarray(
        table_vectors,
        dtype="float32",
    )

    if table_vectors.ndim != 2:
        raise ValueError(
            "Table embeddings must be 2-D; "
            f"got {table_vectors.shape}"
        )

    table_index = faiss.IndexFlatIP(
        table_vectors.shape[1]
    )

    table_index.add(
        table_vectors
    )

    # =========================================================================
    # Pass 2: collect all row texts
    # =========================================================================

    row_units = build_row_retrieval_units(
        tables
    )

    all_row_texts = []
    all_row_metadata = []
    table_ranges = {}

    cursor = 0

    for table_key, payload in row_units.items():

        texts = payload["rows"]
        metadata = payload["metadata"]

        if not texts:
            continue

        start = cursor
        end = cursor + len(texts)

        table_ranges[table_key] = (
            start,
            end,
        )

        all_row_texts.extend(texts)
        all_row_metadata.extend(metadata)

        cursor = end

    if not all_row_texts:
        return {
            "table_index": table_index,
            "table_metadata": table_metadata,
            "row_indices": {},
            "row_metadata": {},
        }

    print(
        f"Row-level units: "
        f"{len(all_row_texts):,}"
    )

    # =========================================================================
    # Embed all rows
    # =========================================================================

    row_vectors = embed_model.encode(
        all_row_texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    row_vectors = np.asarray(
        row_vectors,
        dtype="float32",
    )

    if row_vectors.ndim != 2:
        raise ValueError(
            "Row embeddings must be 2-D; "
            f"got {row_vectors.shape}"
        )

    if len(row_vectors) != len(
        all_row_metadata
    ):
        raise RuntimeError(
            "Row embedding/metadata mismatch: "
            f"{len(row_vectors):,} vectors vs "
            f"{len(all_row_metadata):,} metadata."
        )

    # =========================================================================
    # Build one FAISS row index per table
    # =========================================================================

    row_indices = {}
    row_metadata = {}

    for table_key, (
        start,
        end,
    ) in table_ranges.items():

        vectors = row_vectors[
            start:end
        ]

        metadata = all_row_metadata[
            start:end
        ]

        if len(vectors) == 0:
            continue

        index = faiss.IndexFlatIP(
            vectors.shape[1]
        )

        index.add(vectors)

        row_indices[
            table_key
        ] = index

        row_metadata[
            table_key
        ] = metadata

    # =========================================================================
    # Consistency checks
    # =========================================================================

    total_row_vectors = sum(
        index.ntotal
        for index in row_indices.values()
    )

    if total_row_vectors != len(
        all_row_metadata
    ):
        raise RuntimeError(
            "Row FAISS mismatch: "
            f"{total_row_vectors:,} indexed vs "
            f"{len(all_row_metadata):,} metadata."
        )

    if table_index.ntotal != len(
        table_metadata
    ):
        raise RuntimeError(
            "Table FAISS mismatch: "
            f"{table_index.ntotal:,} indexed vs "
            f"{len(table_metadata):,} metadata."
        )

    print(
        f"Tables indexed : "
        f"{table_index.ntotal:,}"
    )

    print(
        f"Row indices    : "
        f"{len(row_indices):,}"
    )

    print(
        f"Rows indexed   : "
        f"{total_row_vectors:,}"
    )

    return {
        "table_index": table_index,
        "table_metadata": table_metadata,
        "row_indices": row_indices,
        "row_metadata": row_metadata,
    }


# =============================================================================
# Phase 2d: Hierarchical retrieval
# =============================================================================

def search_table_rows(
    query,
    embed_model,
    retrieval_index,
    table_top_k=5,
    row_top_k=5,
):
    """
    Hierarchical table → row retrieval.

    The query is embedded once and reused at both levels.
    """

    table_index = retrieval_index[
        "table_index"
    ]

    table_metadata = retrieval_index[
        "table_metadata"
    ]

    row_indices = retrieval_index[
        "row_indices"
    ]

    row_metadata = retrieval_index[
        "row_metadata"
    ]

    if (
        table_index is None
        or table_index.ntotal == 0
    ):
        return []

    # -------------------------------------------------------------------------
    # Query embedding
    # -------------------------------------------------------------------------

    query_vector = embed_model.encode(
        [query],
        normalize_embeddings=True,
    )

    query_vector = np.asarray(
        query_vector,
        dtype="float32",
    )

    # -------------------------------------------------------------------------
    # Stage 1: candidate tables
    # -------------------------------------------------------------------------

    table_scores, table_ids = (
        table_index.search(
            query_vector,
            min(
                table_top_k,
                table_index.ntotal,
            ),
        )
    )

    results = []

    # -------------------------------------------------------------------------
    # Stage 2: rows inside candidate tables
    # -------------------------------------------------------------------------

    for table_score, table_vector_id in zip(
        table_scores[0],
        table_ids[0],
    ):

        if table_vector_id < 0:
            continue

        table_meta = table_metadata[
            table_vector_id
        ]

        table_key = (
            table_meta["doc_id"],
            table_meta["table_id"],
        )

        row_index = row_indices.get(
            table_key
        )

        if (
            row_index is None
            or row_index.ntotal == 0
        ):
            continue

        row_scores, row_ids = (
            row_index.search(
                query_vector,
                min(
                    row_top_k,
                    row_index.ntotal,
                ),
            )
        )

        for row_score, row_vector_id in zip(
            row_scores[0],
            row_ids[0],
        ):

            if row_vector_id < 0:
                continue

            metadata = row_metadata[
                table_key
            ][row_vector_id]

            result = dict(metadata)

            result["row_score"] = float(
                row_score
            )

            result["table_score"] = float(
                table_score
            )

            # Geometric combination keeps a poor table match from
            # dominating merely because one row happened to score highly.
            result["combined_score"] = (
                float(table_score)
                * float(row_score)
            )

            results.append(result)

    results.sort(
        key=lambda item: item[
            "combined_score"
        ],
        reverse=True,
    )

    return results


# =============================================================================
# Exact structured retrieval
# =============================================================================

def load_table_json(
    result,
    table_store=DEFAULT_TABLE_STORE,
):
    """
    Resolve a retrieval hit to the JSON source of truth.
    """

    path = (
        Path(table_store)
        / (
            f"{result['doc_id']}_"
            f"{result['table_id']}.json"
        )
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def get_retrieved_row(
    result,
    table_store=DEFAULT_TABLE_STORE,
):
    """
    Resolve a row retrieval hit into its exact structured record.
    """

    table = load_table_json(
        result,
        table_store,
    )

    row_id = result["row_id"]

    rows = table.get("data") or []

    if (
        row_id < 0
        or row_id >= len(rows)
    ):
        raise IndexError(
            f"Row {row_id} does not exist in "
            f"{result['doc_id']}_"
            f"{result['table_id']}.json"
        )

    return {
        "table": table,
        "row_id": row_id,
        "row": rows[row_id],
    }


# =============================================================================
# Execution
# =============================================================================

def process_batches(
    batch_dirs,
    results_dir,
    embed_model,
    *,
    max_workers=2,
    batch_size=128,
):
    """
    Process multiple document batches.

    For each batch:
        1. Extract and persist semantic tables / processed HTML.
        2. Build table- and row-level FAISS indices.
        3. Persist the retrieval indices.

    Returns lightweight per-batch results suitable for
    diagnostics, evaluation, or reporting by the caller.
    """

    results_dir = Path(results_dir)
    results_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    batch_reports = []

    for batch_number, batch_dir in enumerate(batch_dirs, start=1):

        batch_dir = Path(batch_dir)
        batch_name = batch_dir.name

        print()
        print("=" * 80)
        print(
            f"PROCESSING BATCH "
            f"[{batch_number}/{len(batch_dirs)}]: "
            f"{batch_name}"
        )
        print("=" * 80)

        try:
            if not batch_dir.is_dir():
                raise FileNotFoundError(
                    f"Batch directory does not exist: {batch_dir}"
                )

            # -------------------------------------------------------------
            # Batch output directories
            # -------------------------------------------------------------

            batch_result_dir = (
                results_dir / batch_name
            )

            table_store = (
                batch_result_dir / "table_store"
            )

            processed_dir = (
                batch_result_dir / "processed_docs"
            )

            index_dir = (
                batch_result_dir / "index"
            )

            # A batch is an independent processing unit.
            if batch_result_dir.exists():
                shutil.rmtree(batch_result_dir)

            table_store.mkdir(
                parents=True,
                exist_ok=True,
            )

            processed_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            index_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            # -------------------------------------------------------------
            # Locate documents
            # -------------------------------------------------------------

            document_files = sorted(
                batch_dir.glob("*.html")
            )

            if not document_files:
                batch_reports.append({
                    "batch": batch_name,
                    "documents": 0,
                    "results": [],
                })
                continue

            # -------------------------------------------------------------
            # Phase 1 — extraction
            # -------------------------------------------------------------

            document_results = list(
                run_batch(
                    document_files,
                    max_workers=max_workers,
                    table_store=str(table_store),
                    processed_dir=str(processed_dir),
                )
            )

            # -------------------------------------------------------------
            # Phase 2 — indexing
            # -------------------------------------------------------------

            tables = []

            for result in document_results:
                if result.get("status") == "success":
                    tables.extend(result.get("tables") or [])

            retrieval_index = build_table_index(
                tables,
                embed_model,
                batch_size=batch_size,
            )

            # -------------------------------------------------------------
            # Persist table index
            # -------------------------------------------------------------

            if retrieval_index["table_index"] is not None:

                faiss.write_index(
                    retrieval_index["table_index"],
                    str(index_dir / "table.index"),
                )

            (index_dir / "table_metadata.json").write_text(
                json.dumps(
                    retrieval_index["table_metadata"],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            # -------------------------------------------------------------
            # Persist row indices
            # -------------------------------------------------------------

            row_index_dir = (
                index_dir / "rows"
            )

            row_index_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            row_metadata = {}

            for table_key, row_index in (
                retrieval_index["row_indices"].items()
            ):

                doc_id, table_id = table_key

                index_name = (
                    f"{doc_id}__{table_id}.index"
                )

                faiss.write_index(
                    row_index,
                    str(row_index_dir / index_name),
                )

                row_metadata[
                    f"{doc_id}__{table_id}"
                ] = retrieval_index[
                    "row_metadata"
                ][table_key]

            (index_dir / "row_metadata.json").write_text(
                json.dumps(
                    row_metadata,
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )

            # -------------------------------------------------------------
            # Return lightweight results
            # -------------------------------------------------------------

            batch_reports.append({
                "batch": batch_name,
                "documents": len(document_results),
                "results": document_results,
            })

            # -------------------------------------------------------------
            # Release batch-specific memory
            # -------------------------------------------------------------

            del retrieval_index
            del tables
            del document_results
            gc.collect()

        except Exception as exc:
            try:
                if batch_result_dir.exists():
                    shutil.rmtree(batch_result_dir)
            except Exception:
                pass

            batch_reports.append({
                "batch": batch_name,
                "status": "failed",
                "error": str(exc),
            })

            gc.collect()
            continue

    return batch_reports