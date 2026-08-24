import logging
import re
import time
import unicodedata
from pathlib import Path
from typing import Iterable

from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    HTMLFormatOption,
    PdfFormatOption,
)
from docling.datamodel.document import ConversionResult


_log = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Normalize Unicode and remove unwanted control characters."""

    if not text:
        return text

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "\u00A0": " ",   # Non-breaking space
        "\u202F": " ",   # Narrow non-breaking space
        "\u2009": " ",   # Thin space
        "\u2007": " ",   # Figure space
        "\x00": "",      # Null byte
        "\ufffd": "",    # Unicode replacement character
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove control characters while preserving newlines and tabs.
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)


def create_document_converter() -> DocumentConverter:
    """Create and configure the Docling document converter."""

    pdf_pipeline_options = PdfPipelineOptions()
    pdf_pipeline_options.generate_page_images = True

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.HTML,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_pipeline_options,
                backend=DoclingParseV4DocumentBackend,
            ),
            InputFormat.HTML: HTMLFormatOption(),
        },
    )


def export_documents(
    conversion_results: Iterable[ConversionResult],
    output_dir: Path,
) -> tuple[int, int, int]:
    """Export successfully converted documents and report conversion status."""

    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    partial_success_count = 0
    failure_count = 0

    for result in conversion_results:
        if result.status == ConversionStatus.SUCCESS:
            success_count += 1

            doc_filename = result.input.file.stem
            output_path = output_dir / f"{doc_filename}.md"

            markdown = clean_text(
                result.document.export_to_markdown()
            )

            output_path.write_text(
                markdown,
                encoding="utf-8",
            )

        elif result.status == ConversionStatus.PARTIAL_SUCCESS:
            partial_success_count += 1

            _log.warning(
                "Document %s was partially converted:",
                result.input.file,
            )

            for error in result.errors:
                _log.warning(
                    "\t%s",
                    error.error_message,
                )

        else:
            failure_count += 1

            _log.error(
                "Document %s failed to convert.",
                result.input.file,
            )

    total_count = (
        success_count
        + partial_success_count
        + failure_count
    )

    _log.info(
        "Processed %d documents: %d succeeded, %d partially succeeded, %d failed.",
        total_count,
        success_count,
        partial_success_count,
        failure_count,
    )

    return (
        success_count,
        partial_success_count,
        failure_count,
    )


def convert_documents(
    input_dir: Path,
    output_dir: Path,
) -> None:
    """Convert all supported documents in an input directory."""

    input_doc_paths = [
        path
        for path in input_dir.iterdir()
        if path.is_file()
    ]

    converter = create_document_converter()

    start_time = time.perf_counter()

    conversion_results = converter.convert_all(
        input_doc_paths,
        raises_on_error=False,
    )

    _, _, failure_count = export_documents(
        conversion_results,
        output_dir,
    )

    elapsed_time = time.perf_counter() - start_time

    _log.info(
        "Document conversion completed in %.2f seconds.",
        elapsed_time,
    )

    if failure_count > 0:
        raise RuntimeError(
            f"{failure_count}/{len(input_doc_paths)} documents "
            "failed to convert."
        )