"""utils/pdf_to_image.py — Render PDF pages as images using PyMuPDF (fitz)"""
import os

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False


def pdf_to_images(input_path: str, output_dir: str,
                  out_prefix: str = 'page',
                  fmt: str = 'jpg',
                  dpi: int = 150) -> list[str]:
    """
    Render each page of a PDF as an image file.

    Parameters
    ----------
    input_path  : path to the input PDF
    output_dir  : directory where images will be saved
    out_prefix  : filename prefix (e.g. 'page' → 'page_001.jpg')
    fmt         : output format — 'jpg' or 'png'
    dpi         : rendering resolution (default 150 dpi)

    Returns a list of absolute paths to the created image files.
    Raises ImportError if PyMuPDF (pymupdf) is not installed.
    """
    if not FITZ_AVAILABLE:
        raise ImportError(
            "PyMuPDF is required for PDF→Image conversion. "
            "Run: pip install pymupdf"
        )

    fmt = fmt.lower().replace('jpeg', 'jpg')
    if fmt not in ('jpg', 'png'):
        fmt = 'jpg'

    ext     = 'jpg' if fmt == 'jpg' else 'png'
    zoom    = dpi / 72            # 72 is the default PDF DPI
    matrix  = fitz.Matrix(zoom, zoom)

    doc     = fitz.open(input_path)
    results = []

    for i, page in enumerate(doc):
        pix      = page.get_pixmap(matrix=matrix, alpha=False)
        out_path = os.path.join(output_dir, f'{out_prefix}_{i + 1:03d}.{ext}')

        if fmt == 'jpg':
            pix.save(out_path, jpg_quality=85)
        else:
            pix.save(out_path)

        results.append(out_path)

    doc.close()
    return results
