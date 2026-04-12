"""
merge_service.py - Merges multiple PDF files into a single PDF document.
Uses PyPDF2 (or pypdf) for merging.
"""

import os
import uuid
from config import Config
from utils.helper import get_upload_path
from models.document_model import (
    get_document_by_id,
    insert_merged_document
)

try:
    # Try newer pypdf first, fall back to PyPDF2
    from pypdf import PdfWriter, PdfReader
    PDF_LIB = 'pypdf'
except ImportError:
    try:
        from PyPDF2 import PdfWriter, PdfReader
        PDF_LIB = 'PyPDF2'
    except ImportError:
        PDF_LIB = None


def merge_pdfs(doc_ids):
    """
    Merge the PDF files corresponding to the given document IDs.

    Each document must be converted to PDF before merging;
    uses the 'converted_name' field from the database.

    Returns:
        dict with 'success', 'message', and on success:
            'merged_name', 'merged_path', 'merged_id'
    """
    if PDF_LIB is None:
        return {
            'success': False,
            'message': 'PDF library not installed. Run: pip install pypdf'
        }

    if not doc_ids or len(doc_ids) < 2:
        return {
            'success': False,
            'message': 'Please select at least 2 documents to merge.'
        }

    writer = PdfWriter()
    source_ids = []
    errors = []

    for doc_id in doc_ids:
        # Fetch document record from DB
        doc = get_document_by_id(doc_id)
        if not doc:
            errors.append(f'Document ID {doc_id} not found in database.')
            continue

        # Determine which file to use (converted PDF if available)
        pdf_filename = doc.get('converted_name') or doc.get('stored_name')
        if not pdf_filename:
            errors.append(f'No file found for document ID {doc_id}.')
            continue

        pdf_path = get_upload_path(pdf_filename)

        # Verify the file exists on disk
        if not os.path.exists(pdf_path):
            errors.append(
                f'File "{pdf_filename}" for document ID {doc_id} '
                f'does not exist on disk.'
            )
            continue

        # Verify the file has a .pdf extension
        if not pdf_filename.lower().endswith('.pdf'):
            errors.append(
                f'Document "{doc.get("original_name", pdf_filename)}" '
                f'(ID {doc_id}) has not been converted to PDF yet. '
                f'Please convert it first.'
            )
            continue

        try:
            # Append all pages from this PDF to the writer
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                writer.add_page(page)
            source_ids.append(doc_id)
        except Exception as e:
            errors.append(
                f'Failed to read "{pdf_filename}" (ID {doc_id}): {str(e)}'
            )

    # Check we have at least 2 valid PDFs to merge
    if len(source_ids) < 2:
        error_detail = '; '.join(errors) if errors else 'Not enough valid PDFs.'
        return {
            'success': False,
            'message': f'Need at least 2 valid PDFs to merge. Issues: {error_detail}'
        }

    # Generate unique output filename
    merged_name = f"merged_{uuid.uuid4().hex[:10]}.pdf"
    merged_path = get_upload_path(merged_name)

    try:
        # Write the merged PDF to disk
        with open(merged_path, 'wb') as out_f:
            writer.write(out_f)

        merged_size = os.path.getsize(merged_path)

        # Save merged document record to DB
        merged_id = insert_merged_document(merged_name, source_ids, merged_size)

        result = {
            'success': True,
            'message': (
                f'Successfully merged {len(source_ids)} PDF(s) into "{merged_name}".'
                + (f' Warnings: {"; ".join(errors)}' if errors else '')
            ),
            'merged_name': merged_name,
            'merged_path': merged_path,
            'merged_id': merged_id,
            'merged_size': merged_size
        }
        return result

    except Exception as e:
        # Clean up output file if writing failed
        if os.path.exists(merged_path):
            os.remove(merged_path)
        return {
            'success': False,
            'message': f'Failed to write merged PDF: {str(e)}'
        }
