"""utils/pdf_split.py — Split a PDF into pages or page ranges"""
import os
from pypdf import PdfWriter, PdfReader


def parse_page_range(range_str: str, total: int) -> list[int]:
    """
    Parse a range string like '1-3,5,7-9' into a sorted list
    of 0-indexed page numbers. Pages outside [1, total] are clamped/ignored.
    """
    pages = set()
    for part in range_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                start = max(1, int(start.strip()))
                end   = min(total, int(end.strip()))
                pages.update(range(start - 1, end))
            except ValueError:
                pass
        else:
            try:
                p = int(part.strip())
                if 1 <= p <= total:
                    pages.add(p - 1)
            except ValueError:
                pass
    return sorted(pages)


def split_pdf(input_path: str, output_dir: str,
              mode: str = 'all', page_range: str = '',
              out_prefix: str = 'page') -> list[str]:
    """
    Split a PDF file.

    mode='all'   → one PDF per page  (returns list of files)
    mode='range' → one PDF containing only the selected pages
    mode='fixed' → split every N pages (page_range = N as string)

    Returns a list of output file paths.
    """
    reader = PdfReader(input_path)
    total  = len(reader.pages)
    results = []

    if mode == 'all':
        # One PDF per page
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out = os.path.join(output_dir, f'{out_prefix}_page_{i + 1:03d}.pdf')
            with open(out, 'wb') as f:
                writer.write(f)
            results.append(out)

    elif mode == 'range':
        # Selected pages into one PDF
        pages = parse_page_range(page_range, total)
        if not pages:
            raise ValueError('Invalid or empty page range.')
        writer = PdfWriter()
        for p in pages:
            writer.add_page(reader.pages[p])
        out = os.path.join(output_dir, f'{out_prefix}_range.pdf')
        with open(out, 'wb') as f:
            writer.write(f)
        results.append(out)

    elif mode == 'fixed':
        # Split every N pages
        try:
            n = max(1, int(page_range))
        except (ValueError, TypeError):
            n = 1
        chunk = 0
        for start in range(0, total, n):
            chunk += 1
            writer = PdfWriter()
            for i in range(start, min(start + n, total)):
                writer.add_page(reader.pages[i])
            out = os.path.join(output_dir, f'{out_prefix}_part_{chunk:03d}.pdf')
            with open(out, 'wb') as f:
                writer.write(f)
            results.append(out)

    else:
        raise ValueError(f'Unknown split mode: {mode}')

    return results
