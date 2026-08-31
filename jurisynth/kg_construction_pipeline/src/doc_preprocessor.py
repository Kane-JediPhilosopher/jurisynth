from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import re
import gc
import requests
import shutil

import faiss
import numpy as np
from lxml import html
import base64
import hashlib

# =============================================================================
# Configuration
# =============================================================================

DEFAULT_TABLE_STORE = "table_store"
DEFAULT_IMAGE_STORE = "image_store"
DEFAULT_PROCESSED_DIR = "processed_docs"


# =============================================================================
# Helper functions
# =============================================================================

def normalize_cell_text(value):
    """Normalize cell text for conservative comparison."""

    return re.sub(
        r"\s+",
        " ",
        str(value).strip().lower(),
    )


def is_oj_table(table):
    """
    Return True if the table is explicitly marked as a genuine
    semantic OJ table via the custom 'oj-table' class.
    """
    classes = table.get("class", "").split()
    return "oj-table" in classes


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


def extract_header_rows(table):
    """
    Extract the leading structural header block from an OJ table.

    OJ documents identify header cells using the custom ``oj-tbl-hdr``
    class, which may occur on descendants such as <p> inside <td>.

    A row is considered an explicit OJ header row only when:
        - it contains at least one oj-tbl-hdr marker, and
        - every non-empty cell in that row is either oj-tbl-hdr-marked
          or a conventional <th>.

    This prevents later semantic grouping/category rows from being
    misclassified as global table headers.

    Supports:
        - oj-tbl-hdr
        - <thead>
        - <th> fallback
        - colspan
        - rowspan

    Returns:
        list[list[str]]
    """

    # -----------------------------------------------------------------
    # Helpers
    # -----------------------------------------------------------------

    def cell_has_oj_header(cell):
        return bool(
            cell.xpath(
                ".//*[contains("
                "concat(' ', normalize-space(@class), ' '), "
                "' oj-tbl-hdr ')]"
            )
        )

    def cell_text(cell):
        return get_direct_cell_text(cell).strip()

    def span_value(cell, name):
        try:
            value = int(cell.get(name, "1"))
        except (TypeError, ValueError):
            value = 1

        return max(value, 1)

    # -----------------------------------------------------------------
    # Candidate physical rows.
    # -----------------------------------------------------------------

    candidate_rows = table.xpath(
        "./tr | ./thead/tr | ./tbody/tr | ./tfoot/tr"
    )

    if not candidate_rows:
        return []

    # -----------------------------------------------------------------
    # Find explicit leading OJ header block.
    #
    # IMPORTANT:
    # Merely containing oj-tbl-hdr is not enough. OJ documents also
    # use that class on semantic grouping rows inside table bodies.
    # -----------------------------------------------------------------

    header_rows = []
    using_oj_headers = False

    for tr in candidate_rows:
        cells = tr.xpath("./td | ./th")

        if not cells:
            if header_rows:
                break
            continue

        has_oj_header = any(
            cell_has_oj_header(cell)
            for cell in cells
        )

        if not has_oj_header:
            if header_rows:
                break
            break

        # Every meaningful cell must participate in the header.
        structurally_header = True

        for cell in cells:
            text = cell_text(cell)

            # Empty spacer cells are allowed.
            if not text:
                continue

            if (
                cell.tag != "th"
                and not cell_has_oj_header(cell)
            ):
                structurally_header = False
                break

        if not structurally_header:
            break

        using_oj_headers = True
        header_rows.append(tr)

    # -----------------------------------------------------------------
    # No valid explicit OJ header block.
    # Fall back to conventional HTML header structure.
    # -----------------------------------------------------------------

    if not header_rows:
        using_oj_headers = False

        header_rows = table.xpath(
            "./thead/tr"
        )

        if not header_rows:
            header_rows = []

            for tr in candidate_rows:
                if tr.xpath("./th"):
                    header_rows.append(tr)

                elif header_rows:
                    break

                else:
                    break

        if not header_rows:
            return []

    # -----------------------------------------------------------------
    # Build logical grid.
    #
    # occupied maps:
    #
    #     (row_index, column_index) -> inherited rowspan text
    #
    # Unlike the old implementation, rowspan content is actually
    # propagated into subsequent logical header rows.
    # -----------------------------------------------------------------

    grid = []
    occupied = {}

    for row_index, tr in enumerate(header_rows):
        row = []

        # Pre-populate columns inherited through rowspan.
        inherited = {
            column: text
            for (occupied_row, column), text
            in occupied.items()
            if occupied_row == row_index
        }

        if inherited:
            width = max(inherited) + 1
            row = [""] * width

            for column, text in inherited.items():
                row[column] = text

        column = 0

        cells = tr.xpath("./td | ./th")

        for cell in cells:
            # ---------------------------------------------------------
            # Find next column not occupied by a rowspan.
            # ---------------------------------------------------------

            while (
                (row_index, column)
                in occupied
            ):
                column += 1

            colspan = span_value(
                cell,
                "colspan",
            )

            rowspan = span_value(
                cell,
                "rowspan",
            )

            is_oj_header = cell_has_oj_header(
                cell
            )

            is_th = cell.tag == "th"

            # ---------------------------------------------------------
            # Header text.
            #
            # For explicit OJ headers, only marked cells contribute
            # semantic text. Blank/unmarked structural cells still
            # consume their proper columns.
            # ---------------------------------------------------------

            if using_oj_headers:
                if is_oj_header:
                    header_nodes = cell.xpath(
                        ".//*[contains("
                        "concat(' ', normalize-space(@class), ' '), "
                        "' oj-tbl-hdr ')]"
                    )

                    text_parts = []

                    for node in header_nodes:
                        text_parts.extend(
                            node.itertext()
                        )

                    text = " ".join(
                        " ".join(
                            text_parts
                        ).split()
                    )

                elif is_th:
                    text = cell_text(cell)

                else:
                    text = ""

            else:
                text = cell_text(cell)

            # ---------------------------------------------------------
            # Ensure logical row width.
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
            # Place cell and propagate rowspan.
            # ---------------------------------------------------------

            for offset in range(colspan):
                target_column = (
                    column + offset
                )

                row[target_column] = text

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
                        ] = text

            column += colspan

        if row:
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
                normalize_cell_text(value) == normalize_cell_text(existing)
                for existing in parts
            ):
                continue

            parts.append(value)

        flattened.append(
            " | ".join(parts)
        )

    return flattened


def get_direct_rows(table):
    """
    Return <tr> elements belonging directly to this table.

    Rows belonging to nested tables are excluded.
    """
    return table.xpath(
        "./tr | ./thead/tr | ./tbody/tr | ./tfoot/tr"
    )


def extract_direct_row(row):
    """
    Extract the direct cells of a row.

    Nested tables remain inside their containing cell and are not
    treated as additional cells.
    """
    return row.xpath("./td | ./th")


def get_direct_cell_text(cell):
    """
    Extract text belonging directly to a cell while excluding
    all text contained inside nested tables.
    """
    parts = []

    # Text directly contained in the cell itself.
    if cell.text:
        parts.append(cell.text)

    for node in cell.iterdescendants():
        # Skip nested table subtrees entirely.
        if node.tag == "table":
            continue

        parent = node.getparent()
        inside_nested_table = False

        while parent is not None and parent is not cell:
            if parent.tag == "table":
                inside_nested_table = True
                break
            parent = parent.getparent()

        if inside_nested_table:
            continue

        if node.text:
            parts.append(node.text)

    return " ".join(" ".join(parts).split())


def build_table_description(table):
    """
    Build a deterministic semantic description for an OJ table.

    Priority:
        1. Explicit table title / heading
        2. Column headers
        3. First informative data rows
        4. Surrounding table context

    The result is intended as a compact semantic description for
    retrieval and later RDF representation, not as a generated title.
    """

    parts = []

    # -------------------------------------------------------------------------
    # 1. Explicit table title
    # -------------------------------------------------------------------------

    title = table.get("title")

    if title:
        title = str(title).strip()
        if title:
            parts.append(title)

    # -------------------------------------------------------------------------
    # 2. Column headers
    # -------------------------------------------------------------------------

    header = table.get("header")

    if header:
        headers = [
            str(column).strip()
            for column in header
            if str(column).strip()
        ]

        if headers:
            parts.append(" | ".join(headers))

    # -------------------------------------------------------------------------
    # 3. First informative data rows
    #
    # Keep this deliberately small. We want distinctive semantic content,
    # not the entire table duplicated into the description.
    # -------------------------------------------------------------------------

    data = table.get("data") or []

    informative_rows = []

    for row in data:
        cells = [
            str(cell).strip()
            for cell in row
            if str(cell).strip()
        ]

        if not cells:
            continue

        row_text = " | ".join(cells)

        # Avoid adding rows that merely duplicate the header.
        if header:
            header_text = " | ".join(
                str(column).strip()
                for column in header
                if str(column).strip()
            )
            if row_text == header_text:
                continue

        informative_rows.append(row_text)

        if len(informative_rows) >= 3:
            break

    if informative_rows:
        parts.append(" | ".join(informative_rows))

    # -------------------------------------------------------------------------
    # 4. Surrounding context
    #
    # This is deliberately last: table-specific content should dominate.
    # -------------------------------------------------------------------------

    context = table.get("context")

    if context:
        context = str(context).strip()
        if context:
            parts.append(context)

    # -------------------------------------------------------------------------
    # Deduplicate while preserving priority order.
    # -------------------------------------------------------------------------

    seen = set()
    unique_parts = []

    for part in parts:
        normalized = " ".join(part.split())

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        unique_parts.append(normalized)

    return " — ".join(unique_parts)


def get_nested_oj_tables(table):
    """
    Return genuine OJ tables nested anywhere inside this table.

    The table itself is excluded from the result.
    """
    return [
        nested
        for nested in table.xpath(".//table")
        if is_oj_table(nested)
    ]


def extract_oj_table(
    table,
    doc_id,
    table_id,
    context=None,
    parent_table_id=None,
):
    header_rows = extract_header_rows(table)

    header_row_ids = {
        id(row)
        for row in header_rows
    }

    rows = []

    direct_rows = get_direct_rows(table)

    header_row_count = len(header_rows)

    for row_index, row in enumerate(direct_rows):
        if row_index < header_row_count:
            continue

        cells = extract_direct_row(row)
        if not cells:
            continue

        logical_row = []

        for cell in cells:
            text = get_direct_cell_text(cell)

            try:
                colspan = int(cell.get("colspan", "1"))
            except (TypeError, ValueError):
                colspan = 1

            colspan = max(colspan, 1)

            logical_row.extend([text] * colspan)

        if logical_row:
            rows.append(logical_row)

    data = rows

    if header_rows:
        header = flatten_header_rows(header_rows)
        header_row_count = len(header_rows)
    else:
        header = None
        header_row_count = 0

    result = {
        "doc_id": doc_id,
        "table_id": table_id,
        "parent_table_id": parent_table_id,
        "description": None,
        "context": context,
        "header": header,
        "data": data,
        "children": [],
    }

    result["description"] = build_table_description(result)

    return result


def linearize_non_oj_table(
    table,
    preserve_blocks=False,
):
    """
    Recursively linearize a non-OJ table into readable plain text.

    When preserve_blocks=True, preserve paragraph/list/heading
    boundaries inside cells instead of collapsing the entire cell
    into one text string.
    """

    lines = []

    for row in get_direct_rows(table):
        cells = extract_direct_row(row)

        for cell in cells:

            if preserve_blocks:
                blocks = cell.xpath(
                    ".//p | .//h1 | .//h2 | .//h3 | "
                    ".//h4 | .//h5 | .//h6 | .//li"
                )

                for block in blocks:
                    # Skip blocks belonging to nested tables.
                    parent = block.getparent()
                    inside_nested_table = False

                    while parent is not None and parent is not cell:
                        if parent.tag == "table":
                            inside_nested_table = True
                            break
                        parent = parent.getparent()

                    if inside_nested_table:
                        continue

                    text = " ".join(
                        " ".join(block.itertext()).split()
                    )

                    if text:
                        lines.append(text)

                # Fallback for cells without recognised block elements.
                if not blocks:
                    direct_text = get_direct_cell_text(cell)

                    if direct_text:
                        lines.append(direct_text)

            else:
                direct_text = get_direct_cell_text(cell)

                if direct_text:
                    lines.append(direct_text)

            for nested in cell.xpath("./table"):

                if is_oj_table(nested):
                    continue

                nested_text = linearize_non_oj_table(
                    nested,
                    preserve_blocks=preserve_blocks,
                )

                if nested_text:
                    lines.append(nested_text)

    return "\n".join(lines)


def preprocess_docs(
    document,
    doc_id,
):
    """
    Preprocess one parsed EU legislation HTML document.

    Genuine OJ semantic tables (class='oj-tables') are extracted as
    structured tables. Nested genuine OJ tables are extracted
    independently and linked to their parent table through
    parent_table_id, parent_row, and parent_cell.

    Non-OJ tables are treated as formatting/layout structures and
    linearized into ordinary document text.

    Returns:
        A list of JSON-compatible semantic table dictionaries.
    """

    tables = []
    table_counter = 0

    # -------------------------------------------------------------------------
    # Table ID generation
    # -------------------------------------------------------------------------

    def next_table_id():
        nonlocal table_counter

        table_counter += 1

        return f"table_{table_counter}"

    # -------------------------------------------------------------------------
    # Process a genuine OJ table and recursively process genuine OJ children.
    # -------------------------------------------------------------------------

    def process_oj_table(
        table,
        parent_table_id=None,
        parent_row=None,
        parent_cell=None,
    ):
        table_id = next_table_id()

        extracted = extract_oj_table(
            table,
            doc_id=doc_id,
            table_id=table_id,
            parent_table_id=parent_table_id,
        )

        if parent_row is not None:
            extracted["parent_row"] = parent_row

        if parent_cell is not None:
            extracted["parent_cell"] = parent_cell

        tables.append(extracted)

        # ---------------------------------------------------------------------
        # Process genuine OJ tables nested inside this table.
        # ---------------------------------------------------------------------

        direct_rows = get_direct_rows(table)

        for row_index, row in enumerate(direct_rows):

            cells = extract_direct_row(row)

            for cell_index, cell in enumerate(cells):

                for nested in cell.xpath(".//table"):

                    if not is_oj_table(nested):
                        continue

                    process_oj_table(
                        nested,
                        parent_table_id=table_id,
                        parent_row=row_index,
                        parent_cell=cell_index,
                    )

        # The table has now been fully extracted, including any
        # nested OJ tables. Remove the original HTML subtree so
        # it does not remain in the processed document.
        remove_element(table)

        return extracted

    # -------------------------------------------------------------------------
    # Process tables in document order.
    #
    # Genuine OJ tables are extracted here. Only OJ tables whose nearest
    # table ancestor is NOT another OJ table are processed directly;
    # process_oj_table() recursively handles nested OJ tables.
    #
    # Non-OJ tables are linearized separately.
    # -------------------------------------------------------------------------

    root = document

    for element in list(root.iter("table")):
        if element.getparent() is None:
            continue

        # -------------------------------------------------------------
        # Genuine OJ table
        # -------------------------------------------------------------
        if is_oj_table(element):

            # Determine whether this OJ table is already contained
            # inside another OJ table. If so, its ancestor's
            # process_oj_table() call will handle it.
            parent = element.getparent()
            nested_inside_oj = False

            while parent is not None:
                if parent.tag == "table":
                    nested_inside_oj = is_oj_table(parent)
                    break
                parent = parent.getparent()

            if not nested_inside_oj:
                process_oj_table(element)

            continue

        # -------------------------------------------------------------
        # Non-OJ table
        # -------------------------------------------------------------
        #
        # Do NOT process a non-OJ table here if it contains a genuine
        # OJ table. Its linearization would otherwise destroy the DOM
        # subtree containing that OJ table before it can be extracted.
        #
        # Such tables are handled after all OJ tables have been extracted.
        #
        if element.getparent() is None:
            continue

        contains_oj_table = any(
            is_oj_table(nested)
            for nested in element.xpath(".//table")
        )

        if contains_oj_table:
            continue

        text = linearize_non_oj_table(
            element,
            preserve_blocks=doc_id.startswith("JOL_")
        ).strip()

        if text:
            replace_element_with_text(
                element,
                text,
            )
        else:
            remove_element(element)

    # -------------------------------------------------------------------------
    # Second pass: linearize non-OJ tables that contain extracted OJ tables.
    #
    # OJ tables have already been extracted and removed from consideration.
    # The remaining non-OJ table is now safe to linearize.
    # -------------------------------------------------------------------------

    for element in list(root.iter("table")):

        if is_oj_table(element):
            continue

        if element.getparent() is None:
            continue

        text = linearize_non_oj_table(
            element,
            preserve_blocks=doc_id.startswith("JOL_"),
        ).strip()

        if text:
            replace_element_with_text(
                element,
                text,
            )
        else:
            remove_element(element)

    return tables


def store_table(
    table,
    storage_dir=DEFAULT_TABLE_STORE,
):
    """
    Persist one extracted OJ table.

    JSON is the source of truth for the table's structured content
    and semantic header. Context is preserved as table-level provenance.
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
        "description": table.get("description"),   # ADD / KEEP
        "header": table.get("header"),
        "data": table.get("data", []),
    }

    path = (
        storage_path
        / f"{table['doc_id']}_{table['table_id']}.json"
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


def extract_images(root, image_dir, doc_id):
    """
    Extract embedded and externally referenced images from an lxml HTML tree.

    Successfully extracted images are persisted and removed from the tree.

    Failed extractions are also removed from the tree and recorded as failures.

    Returns:
        list[dict]: Metadata for processed images.
    """

    image_dir = Path(image_dir)
    image_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed = []

    for image_number, img in enumerate(
        root.xpath("//img"),
        start=1,
    ):
        src = img.get("src", "")

        encoded = None
        image_data = None

        metadata = {
            "alt": img.get("alt"),
        }

        try:
            # -------------------------------------------------------------
            # Embedded image
            # -------------------------------------------------------------

            if src.startswith("data:image/"):
                header, encoded = src.split(",", 1)

                mime_type = (
                    header
                    .split(";")[0]
                    .split("/", 1)[1]
                )

                image_data = base64.b64decode(
                    encoded,
                    validate=True,
                )

                source_type = "embedded"

            # -------------------------------------------------------------
            # External image
            # -------------------------------------------------------------

            elif src.startswith(("http://", "https://")):
                with requests.get(
                    src,
                    timeout=30,
                ) as response:
                    response.raise_for_status()
                    image_data = response.content

                    content_type = (
                        response.headers
                        .get("Content-Type", "")
                        .split(";", 1)[0]
                    )

                if not content_type.startswith("image/"):
                    raise ValueError(
                        f"URL did not return an image: {content_type}"
                    )

                mime_type = content_type.split("/", 1)[1]
                source_type = "external"

                metadata["source_url"] = src

            # -------------------------------------------------------------
            # Unsupported source
            # -------------------------------------------------------------

            else:
                raise ValueError(
                    f"Unsupported image source: {src[:100]}"
                )

            # -------------------------------------------------------------
            # Persist image
            # -------------------------------------------------------------

            image_hash = hashlib.sha256(
                image_data
            ).hexdigest()

            filename = (
                f"{doc_id}_image_{image_number:03d}.{mime_type}"
            )

            image_path = image_dir / filename

            if not image_path.exists():
                image_path.write_bytes(image_data)

            metadata.update({
                "status": "success",
                "source_type": source_type,
                "filename": filename,
                "path": str(image_path),
                "mime_type": f"image/{mime_type}",
                "sha256": image_hash,
            })

        except Exception as exc:
            metadata.update({
                "status": "failed",
                "error": str(exc),
            })

            if src.startswith(("http://", "https://")):
                metadata["source_url"] = src

        finally:
            # Images must never survive in the processed HTML.
            parent = img.getparent()

            if parent is not None:
                parent.remove(img)

            image_data = None
            encoded = None

        processed.append(metadata)

    return processed


def persist_image_metadata(image_metadata, output_path):
    """
    Persist extracted image metadata as JSON.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            image_metadata,
            f,
            ensure_ascii=False,
            indent=2,
        )


def process_images(root, image_dir, metadata_path, doc_id):
    """
    Extract images, remove them from the HTML tree,
    and persist image metadata.
    """

    metadata = extract_images(
        root,
        image_dir,
        doc_id,
    )

    persist_image_metadata(
        metadata,
        metadata_path,
    )


# =============================================================================
# Per-document worker
# =============================================================================

def extract_only(
    html_path,
    doc_id,
    table_store=DEFAULT_TABLE_STORE,
    image_store=DEFAULT_IMAGE_STORE,
    processed_dir=DEFAULT_PROCESSED_DIR,
):
    """
    Run the complete HTML preprocessing and extraction phase for one
    document.

    Genuine OJ tables are extracted into structured JSON.
    Non-OJ tables are linearized into document text.
    Images are processed separately.

    No FAISS, NumPy, or embedding state is created here.
    """

    html_path = Path(html_path)

    document = html.parse(
        str(html_path),
    )

    # Process/remove images first to reduce DOM memory.
    image_metadata_path = (
        Path(image_store)
        / f"{doc_id}.json"
    )

    process_images(
        root=document.getroot(),
        image_dir=image_store,
        metadata_path=image_metadata_path,
        doc_id=doc_id,
    )

    tables = preprocess_docs(
        document=document,
        doc_id=doc_id,
    )

    if doc_id.startswith("JOL_"):
        root = document.getroot()

        for txt_te in root.xpath("//txt_te"):
            txt_te.tag = "div"

            parent = txt_te.getparent()

            if parent is not None and parent.tag == "p":
                grandparent = parent.getparent()

                if grandparent is not None:
                    parent_index = grandparent.index(parent)

                    parent.remove(txt_te)
                    grandparent.insert(parent_index, txt_te)

                    if (
                        not (parent.text or "").strip()
                        and len(parent) == 0
                    ):
                        grandparent.remove(parent)

    # -------------------------------------------------------------------------
    # Diagnostics
    # -------------------------------------------------------------------------

    semantic_tables = len(tables)

    semantic_rows = sum(
        len(table.get("data") or [])
        for table in tables
    )

    headerless_semantic_tables = sum(
        not table.get("header")
        for table in tables
    )

    nested_semantic_tables = sum(
        table.get("parent_table_id") is not None
        for table in tables
    )

    diagnostics = {
        "semantic_tables": semantic_tables,
        "semantic_rows": semantic_rows,
        "headerless_semantic_tables":
            headerless_semantic_tables,
        "nested_semantic_tables":
            nested_semantic_tables,
    }

    # -------------------------------------------------------------------------
    # Persist semantic tables
    # -------------------------------------------------------------------------

    for table in tables:
        store_table(
            table,
            table_store,
        )

    # -------------------------------------------------------------------------
    # Persist processed HTML
    # -------------------------------------------------------------------------

    output_dir = Path(
        processed_dir,
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_dir
        / f"{doc_id}.html"
    )

    # Special Case
    serialized_html = html.tostring(
        document.getroot(),
        encoding="unicode",
        method="html"
    )

    output_path.write_text(
        serialized_html,
        encoding="utf-8",
    )

    # -------------------------------------------------------------------------
    # Remove non-picklable / unnecessary state
    # -------------------------------------------------------------------------

    del document
    gc.collect()

    # -------------------------------------------------------------------------
    # Return picklable data only
    # -------------------------------------------------------------------------

    return {
        "doc_id": doc_id,
        "processed_path": str(
            output_path,
        ),
        "tables": tables,
        "diagnostics": diagnostics,
    }


# =============================================================================
# Phase 1: Parallel extraction
# =============================================================================

def run_batch(
    batch_files,
    max_workers=2,
    table_store=DEFAULT_TABLE_STORE,
    image_store=DEFAULT_IMAGE_STORE,
    processed_dir=DEFAULT_PROCESSED_DIR
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
                html_path=path,
                doc_id=path.stem,
                table_store=table_store,
                image_store=image_store,
                processed_dir=processed_dir,
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

    if table.get("description"):
        parts.append(str(table["description"]).strip())

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

    return " — ".join(
        part for part in parts if part
    ).strip()


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
            "description": table.get("description")
        })

    return texts, metadata


# =============================================================================
# Phase 2b: Row retrieval text
# =============================================================================

def build_row_retrieval_text(row, header=None):
    """
    Build a semantically self-describing row embedding representation.

    Column headers are prefixed to their corresponding cell values so
    that row-level retrieval retains the table's column semantics.
    """

    parts = []

    for index, cell in enumerate(row):
        cell_text = str(cell).strip()

        if not cell_text:
            continue

        if header and index < len(header):
            header_text = str(header[index]).strip()

            if header_text:
                parts.append(
                    f"{header_text}: {cell_text}"
                )
                continue

        parts.append(cell_text)

    return " | ".join(parts)


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

        row_texts = []
        row_metadata = []

        for row_id, row in enumerate(rows):

            text = build_row_retrieval_text(
                row,
                table.get("header"),
            )

            if not text:
                continue

            row_texts.append(text)
            row_metadata.append(
                {
                    "doc_id": table["doc_id"],
                    "table_id": table["table_id"],
                    "row_id": row_id,
                    "type": "row",
                }
            )

        if row_texts:
            units[table_key] = {
                "rows": row_texts,
                "metadata": row_metadata,
        }

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

    table_index.add(table_vectors)

    del table_vectors
    del table_texts
    gc.collect()

    print(f"Tables indexed: {table_index.ntotal:,}")
    print(f"Table metadata: {len(table_metadata):,}")

    # =========================================================================
    # Pass 2: collect all row texts
    # =========================================================================

    row_units = build_row_retrieval_units(
        tables
    )

    # Only build row indices for tables that are actually
    # represented in the table-level FAISS index.
    indexed_table_keys = {
        (
            metadata["doc_id"],
            metadata["table_id"],
        )
        for metadata in table_metadata
    }

    print(
        f"Row-indexable tables: "
        f"{len(row_units):,}"
    )

    row_units = {
        table_key: payload
        for table_key, payload in row_units.items()
        if table_key in indexed_table_keys
    }

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

    del row_vectors
    del all_row_texts
    del row_units
    del indexed_table_keys
    gc.collect()

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

    del all_row_metadata
    del table_ranges
    gc.collect()

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

            batch_result_dir = results_dir / batch_name
            table_store = batch_result_dir / "table_store"
            image_store = batch_result_dir / "image_store"
            processed_dir = batch_result_dir / "processed_docs"
            index_dir = batch_result_dir / "index"

            # A batch is an independent processing unit.
            if batch_result_dir.exists():
                shutil.rmtree(batch_result_dir)

            table_store.mkdir(
                parents=True,
                exist_ok=True,
            )

            image_store.mkdir(
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
                    image_store=str(image_store),
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

            # -------------------------------------------------------------------------
            # Reduce document results to lightweight reporting data
            # -------------------------------------------------------------------------

            lightweight_results = []

            for result in document_results:
                lightweight = {
                    "doc_id": result["doc_id"],
                    "status": result.get("status"),
                }

                if result.get("status") == "success":
                    lightweight["processed_path"] = result.get(
                        "processed_path"
                    )
                    lightweight["diagnostics"] = result.get(
                        "diagnostics", {}
                    )
                else:
                    lightweight["error"] = result.get(
                        "error"
                    )

                lightweight_results.append(lightweight)

            batch_reports.append({
                "batch": batch_name,
                "status": "success",
                "documents": len(document_results),
                "results": lightweight_results,
            })

            # -------------------------------------------------------------
            # Release batch-specific memory
            # -------------------------------------------------------------

            del retrieval_index
            del tables
            del document_results
            del lightweight_results
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

