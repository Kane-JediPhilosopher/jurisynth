import pytest
from unittest.mock import patch

from pathlib import Path
from types import SimpleNamespace


from docling.datamodel.base_models import ConversionStatus
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    HTMLFormatOption,
    PdfFormatOption,
)

from doc_converter import (
    clean_text,
    create_document_converter,
    export_documents,
    convert_documents,
)

# =====================================================================
# Text preprocessing
# =====================================================================

@pytest.mark.parametrize(
    "raw, expected",
    [
        ("hello\u00a0world", "hello world"),
        ("hello\u202fworld", "hello world"),
        ("hello\u2009world", "hello world"),
        ("hello\u2007world", "hello world"),
        ("hello\x00world", "helloworld"),
        ("hello\ufffdworld", "helloworld"),
        ("hello\x01world", "helloworld"),
        ("hello\nworld\t!", "hello\nworld\t!"),
    ],
)
def test_clean_text_normalizes_and_removes_unwanted_characters(
    raw,
    expected,
):
    assert clean_text(raw) == expected


def test_clean_text_applies_nfkc_normalization():
    assert clean_text("ＡＢＣ") == "ABC"


def test_clean_text_returns_empty_string_unchanged():
    assert clean_text("") == ""


def test_clean_text_preserves_newlines_and_tabs():
    text = (
        "# Heading\n"
        "\n"
        "First paragraph.\n"
        "\tIndented text.\n"
        "Second paragraph."
    )

    assert clean_text(text) == text


# =====================================================================
# Converter configuration
# =====================================================================

def test_create_document_converter_allows_pdf_and_html():
    converter = create_document_converter()

    assert set(converter.allowed_formats) == {
        InputFormat.PDF,
        InputFormat.HTML,
    }


def test_create_document_converter_configures_pdf_pipeline():
    converter = create_document_converter()

    pdf_options = converter.format_to_options[InputFormat.PDF]

    assert isinstance(pdf_options, PdfFormatOption)
    assert isinstance(pdf_options.pipeline_options, PdfPipelineOptions)
    assert pdf_options.pipeline_options.generate_page_images is True

    assert isinstance(
        converter.format_to_options[InputFormat.HTML],
        HTMLFormatOption,
    )


# =====================================================================
# Exporting documents
# =====================================================================

def test_export_documents_writes_successful_documents(tmp_path):
    document = SimpleNamespace(
        export_to_markdown=lambda: "# Title\n\nHello\u00a0world"
    )

    result = SimpleNamespace(
        status=ConversionStatus.SUCCESS,
        input=SimpleNamespace(
            file=tmp_path / "test.html"
        ),
        document=document,
        errors=[],
    )

    counts = export_documents(
        [result],
        tmp_path / "output",
    )

    output = tmp_path / "output" / "test.md"

    assert counts == (1, 0, 0)
    assert output.exists()
    assert output.read_text(encoding="utf-8") == (
        "# Title\n\nHello world"
    )


def test_export_documents_counts_partial_success(tmp_path, caplog):
    error = SimpleNamespace(
        error_message="Table could not be parsed."
    )

    result = SimpleNamespace(
        status=ConversionStatus.PARTIAL_SUCCESS,
        input=SimpleNamespace(
            file=tmp_path / "test.html"
        ),
        document=None,
        errors=[error],
    )

    counts = export_documents(
        [result],
        tmp_path / "output",
    )

    assert counts == (0, 1, 0)
    assert "Table could not be parsed." in caplog.text


def test_export_documents_counts_failures(tmp_path, caplog):
    result = SimpleNamespace(
        status=ConversionStatus.FAILURE,
        input=SimpleNamespace(
            file=tmp_path / "bad.html"
        ),
        document=None,
        errors=[],
    )

    counts = export_documents(
        [result],
        tmp_path / "output",
    )

    assert counts == (0, 0, 1)
    assert "failed to convert" in caplog.text


# =====================================================================
# Docling functionality
# =====================================================================

def test_convert_documents_converts_html_fixture(tmp_path):
    fixture = (
        Path(__file__).parent
        / "fixtures"
        / "doc_converter"
        / "simple.html"
    )

    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()
    input_file = input_dir / fixture.name
    input_file.write_bytes(fixture.read_bytes())

    convert_documents(
        input_dir,
        output_dir,
    )

    output_file = output_dir / "simple.md"

    assert output_file.exists()

    markdown = output_file.read_text(
        encoding="utf-8"
    )

    assert "Test Document" in markdown
    assert "This is a simple test document." in markdown
    assert "It contains a second paragraph." in markdown


# =====================================================================
# Failure handling
# =====================================================================

def test_convert_documents_raises_when_conversion_fails(
    tmp_path,
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    (input_dir / "test.html").write_text(
        "<html></html>",
        encoding="utf-8",
    )

    with patch(
        "doc_converter.create_document_converter"
    ) as mock_create:

        mock_converter = mock_create.return_value

        mock_converter.convert_all.return_value = []

        with patch(
            "doc_converter.export_documents",
            return_value=(0, 0, 1),
        ):
            with pytest.raises(RuntimeError, match="1/1"):
                convert_documents(
                    input_dir,
                    output_dir,
                )


def test_convert_documents_handles_empty_input_directory(
    tmp_path,
):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"

    input_dir.mkdir()

    with patch(
        "doc_converter.create_document_converter"
    ) as mock_create, patch(
        "doc_converter.export_documents",
        return_value=(0, 0, 0),
    ) as mock_export:

        mock_converter = mock_create.return_value
        mock_converter.convert_all.return_value = []

        convert_documents(
            input_dir,
            output_dir,
        )

        mock_converter.convert_all.assert_called_once_with(
            [],
            raises_on_error=False,
        )

        mock_export.assert_called_once()


def test_export_documents_handles_mixed_conversion_results(
    tmp_path,
):
    success_result = SimpleNamespace(
        status=ConversionStatus.SUCCESS,
        input=SimpleNamespace(
            file=tmp_path / "success.html"
        ),
        document=SimpleNamespace(
            export_to_markdown=lambda: "# Successful"
        ),
        errors=[],
    )

    partial_result = SimpleNamespace(
        status=ConversionStatus.PARTIAL_SUCCESS,
        input=SimpleNamespace(
            file=tmp_path / "partial.html"
        ),
        document=None,
        errors=[
            SimpleNamespace(
                error_message="Minor conversion issue."
            )
        ],
    )

    failure_result = SimpleNamespace(
        status=ConversionStatus.FAILURE,
        input=SimpleNamespace(
            file=tmp_path / "failure.html"
        ),
        document=None,
        errors=[],
    )

    counts = export_documents(
        [
            success_result,
            partial_result,
            failure_result,
        ],
        tmp_path / "output",
    )

    assert counts == (1, 1, 1)

    assert (
        tmp_path / "output" / "success.md"
    ).exists()

    assert not (
        tmp_path / "output" / "partial.md"
    ).exists()

    assert not (
        tmp_path / "output" / "failure.md"
    ).exists()


