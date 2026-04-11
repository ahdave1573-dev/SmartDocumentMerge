"""
convert_service.py - Converts DOCX and TXT files to PDF format
Uses python-docx for DOCX reading and reportlab for PDF generation.
"""

import os
import html
from config import Config
from utils.helper import get_upload_path, get_pdf_name_from_stored
from models.document_model import update_document_converted

# ---- DOCX conversion helpers ----
try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ---- PDF generation helper ----
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def _write_pdf_from_lines(lines, output_path):
    """
    Write a list of text lines to a PDF file using ReportLab.
    Each line becomes a paragraph in the PDF.
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab is not installed. Run: pip install reportlab"
        )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )
    styles = getSampleStyleSheet()
    story = []

    for line in lines:
        stripped = line.strip()
        if stripped:
            # Escape HTML special chars (<, >, &) so ReportLab's XML parser
            # does not crash on code, formulas, or angle-bracket content.
            safe_text = html.escape(stripped)
            story.append(Paragraph(safe_text, styles['Normal']))
        else:
            # Empty lines become small spacers
            story.append(Spacer(1, 0.3 * cm))

    # Build the PDF
    doc.build(story)


def convert_txt_to_pdf(doc_id, stored_name):
    """
    Convert a TXT file to PDF.
    Returns dict with success status and output filename.
    """
    input_path = get_upload_path(stored_name)
    output_name = get_pdf_name_from_stored(stored_name)
    output_path = get_upload_path(output_name)

    if not os.path.exists(input_path):
        return {'success': False, 'message': f'Source file not found: {stored_name}'}

    try:
        # Read all lines from the TXT file
        with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        _write_pdf_from_lines(lines, output_path)

        # Update DB with converted name
        update_document_converted(doc_id, output_name)

        return {
            'success': True,
            'message': 'TXT converted to PDF successfully.',
            'converted_name': output_name
        }

    except Exception as e:
        return {'success': False, 'message': f'TXT conversion failed: {str(e)}'}


def convert_docx_to_pdf(doc_id, stored_name):
    """
    Convert a DOCX file to PDF by extracting text and writing to PDF.
    Returns dict with success status and output filename.
    """
    if not DOCX_AVAILABLE:
        return {
            'success': False,
            'message': 'python-docx is not installed. Run: pip install python-docx'
        }

    input_path = get_upload_path(stored_name)
    output_name = get_pdf_name_from_stored(stored_name)
    output_path = get_upload_path(output_name)

    if not os.path.exists(input_path):
        return {'success': False, 'message': f'Source file not found: {stored_name}'}

    try:
        # Read text content from DOCX
        docx = DocxDocument(input_path)
        lines = [para.text for para in docx.paragraphs]

        _write_pdf_from_lines(lines, output_path)

        # Update DB with converted name
        update_document_converted(doc_id, output_name)

        return {
            'success': True,
            'message': 'DOCX converted to PDF successfully.',
            'converted_name': output_name
        }

    except Exception as e:
        return {'success': False, 'message': f'DOCX conversion failed: {str(e)}'}


def convert_document(doc_id, stored_name, file_type):
    """
    Main entry point for conversion. Routes to the correct converter
    based on file type.
    - PDF files: no conversion needed (already PDF)
    - DOCX: convert via python-docx + reportlab
    - TXT: convert via reportlab
    """
    file_type = file_type.lower()

    if file_type == 'pdf':
        # PDFs are already in the target format; mark as converted
        update_document_converted(doc_id, stored_name)
        return {
            'success': True,
            'message': 'File is already a PDF.',
            'converted_name': stored_name
        }
    elif file_type == 'docx':
        return convert_docx_to_pdf(doc_id, stored_name)
    elif file_type == 'txt':
        return convert_txt_to_pdf(doc_id, stored_name)
    else:
        return {
            'success': False,
            'message': f'Unsupported file type for conversion: {file_type}'
        }
