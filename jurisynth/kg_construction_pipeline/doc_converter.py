import re
import unicodedata
import logging
import time
from collections.abc import Iterable
from pathlib import Path

from docling_core.types.doc.base import ImageRefMode
from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.document import ConversionResult
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, HTMLFormatOption

_log = logging.getLogger(__name__)

# Export toggles:
# - USE_V2 controls modern Docling document exports.
# - USE_LEGACY enables legacy Deep Search exports for comparison or migration.
USE_V2 = True
USE_LEGACY = False

# Cleans documents
def clean_text(text: str) -> str:
    if not text:
        return text

    # 1. Normalize Unicode (fixes odd composed characters)
    text = unicodedata.normalize("NFKC", text)

    # 2. Replace the following:
    replacements = {
        "\u00A0": " ",  # NBSP
        "\u202F": " ",  # narrow NBSP
        "\u202f": " ",  # narrow NBSP
        "\u2009": " ",  # thin space
        "\u2007": " ",  # figure space
        "\x00": "",     # null bytes
        "\ufffd": ""    # Unicode replacement char
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    # 4. Remove control characters (but keep newlines/tabs)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    return text


def export_documents(
    conv_results: Iterable[ConversionResult],
    output_dir: Path,
):
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    failure_count = 0
    partial_success_count = 0

    for conv_res in conv_results:
        if conv_res.status == ConversionStatus.SUCCESS:
            success_count += 1
            doc_filename = conv_res.input.file.stem

            if USE_V2:
                # Export converted files as markdown files
                conv_res.document.save_as_markdown(
                    output_dir / f"{doc_filename}.md",
                    image_mode=ImageRefMode.PLACEHOLDER,
                )
                
                # conv_res.document.save_as_json(
                #     output_dir / f"{doc_filename}.json",
                #     image_mode=ImageRefMode.PLACEHOLDER,
                # )
                
                # conv_res.document.save_as_markdown(
                #     output_dir / f"{doc_filename}.txt",
                #     image_mode=ImageRefMode.PLACEHOLDER,
                #     strict_text=True,
                # )

                # Export Docling document format to markdown:
                with (output_dir / f"{doc_filename}.md").open("w", encoding="utf-8") as fp:
                    raw_md = conv_res.document.export_to_markdown()
                    fp.write(clean_text(raw_md))

                # # Export Docling document format to text:
                # with (output_dir / f"{doc_filename}.txt").open("w") as fp:
                #     fp.write(conv_res.document.export_to_markdown(strict_text=True))

            if USE_LEGACY:
                # Export Markdown format:
                with (output_dir / f"{doc_filename}.legacy.md").open("w", encoding="utf-8") as fp:
                    raw_md = conv_res.document.export_to_markdown()
                    fp.write(clean_text(raw_md))

                # # Export Deep Search document JSON format:
                # with (output_dir / f"{doc_filename}.legacy.json").open(
                #     "w", encoding="utf-8"
                # ) as fp:
                #     fp.write(json.dumps(conv_res.document.export_to_dict()))

                # # Export Text format:
                # with (output_dir / f"{doc_filename}.legacy.txt").open(
                #     "w", encoding="utf-8"
                # ) as fp:
                #     fp.write(
                #         conv_res.document.export_to_markdown(strict_text=True)
                #     )

                # # Export Document Tags format:
                # with (output_dir / f"{doc_filename}.legacy.doctags.txt").open(
                #     "w", encoding="utf-8"
                # ) as fp:
                #     fp.write(conv_res.document.export_to_doctags())

        elif conv_res.status == ConversionStatus.PARTIAL_SUCCESS:
            _log.info(
                f"Document {conv_res.input.file} was partially converted with the following errors:"
            )
            for item in conv_res.errors:
                _log.info(f"\t{item.error_message}")
            partial_success_count += 1
        else:
            _log.info(f"Document {conv_res.input.file} failed to convert.")
            failure_count += 1

    _log.info(
        f"Processed {success_count + partial_success_count + failure_count} docs, "
        f"of which {failure_count} failed "
        f"and {partial_success_count} were partially converted."
    )
    return success_count, partial_success_count, failure_count


def main():
    logging.basicConfig(level=logging.INFO)

    # Location of source documents
    data_folder = Path("../eu_legislation")
    input_doc_paths = [file_path for file_path in data_folder.iterdir()]

    # buf = BytesIO((data_folder / "pdf/2206.01062.pdf").open("rb").read())
    # docs = [DocumentStream(name="my_doc.pdf", stream=buf)]
    # input = DocumentConversionInput.from_streams(docs)

    # # Turn on inline debug visualizations:
    # settings.debug.visualize_layout = True
    # settings.debug.visualize_ocr = True
    # settings.debug.visualize_tables = True
    # settings.debug.visualize_cells = True

    # Configure the PDF pipeline. Enabling page image generation improves HTML
    # previews (embedded images) but adds processing time.
    pdf_pipeline_options = PdfPipelineOptions()
    pdf_pipeline_options.generate_page_images = True

    doc_converter = DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.HTML
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_pipeline_options,
                backend=DoclingParseV4DocumentBackend
            ),
            InputFormat.HTML: HTMLFormatOption()
        }
    )

    start_time = time.time()

    # Convert all inputs. Set `raises_on_error=False` to keep processing other
    # files even if one fails; errors are summarized after the run.
    conv_results = doc_converter.convert_all(
        input_doc_paths,
        raises_on_error=False,  # to let conversion run through all and examine results at the end
    )
    # Write outputs to ./scratch and log a summary.
    _success_count, _partial_success_count, failure_count = export_documents(
        conv_results, output_dir=Path("converted_docs")
    )

    end_time = time.time() - start_time

    _log.info(f"Document conversion complete in {end_time:.2f} seconds.")

    if failure_count > 0:
        raise RuntimeError(
            f"The example failed converting {failure_count} on {len(input_doc_paths)}."
        )

if __name__ == "__main__":
    main()