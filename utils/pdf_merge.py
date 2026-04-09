"""utils/pdf_merge.py — Merge multiple PDFs into one"""
from pypdf import PdfWriter, PdfReader


def merge_pdfs(input_paths: list[str], output_path: str) -> str:
    """
    Merge all PDFs in input_paths into a single PDF at output_path.
    Returns output_path on success.
    """
    writer = PdfWriter()

    for path in input_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, 'wb') as f:
        writer.write(f)

    return output_path
