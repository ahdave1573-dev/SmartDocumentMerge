"""utils/word_to_pdf.py — Convert DOCX/DOC to PDF using python-docx + reportlab"""
import html as html_mod
from docx import Document as DocxDocument
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


def word_to_pdf(input_path: str, output_path: str) -> str:
    """
    Read a DOCX file and produce a PDF at output_path.
    Preserves paragraph text, headings, and bold/italic via basic style mapping.
    """
    # --- Read DOCX ---
    docx = DocxDocument(input_path)

    # --- Set up ReportLab document ---
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        title=input_path,
    )

    styles = getSampleStyleSheet()
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=6,
        textColor=colors.HexColor('#1a202c'),
        fontName='Helvetica-Bold',
    )
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=4,
        fontName='Helvetica',
    )

    story = []

    for para in docx.paragraphs:
        text = para.text.strip()

        if not text:
            story.append(Spacer(1, 0.3 * cm))
            continue

        # Escape HTML special characters for ReportLab XML parser
        safe = html_mod.escape(text)

        # Map DOCX heading styles → ReportLab heading
        if para.style.name.startswith('Heading'):
            story.append(Paragraph(safe, heading_style))
            story.append(HRFlowable(width='100%', thickness=0.5,
                                    color=colors.HexColor('#e2e8f0')))
        else:
            story.append(Paragraph(safe, normal_style))

    # Fallback: if doc is empty
    if not story:
        story.append(Paragraph('(Empty document)', normal_style))

    doc.build(story)
    return output_path
