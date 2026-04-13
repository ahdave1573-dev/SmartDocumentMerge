import fitz
import pdfplumber
from pypdf import PdfReader
from googletrans import Translator
import os
import io
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageOps

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

# Helper to find tesseract
def get_tesseract_path():
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Himansubhai\AppData\Local\Tesseract-OCR\tesseract.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def translate_pdf(input_path, output_path, target_lang):
    """
    Translates PDF while preserving layout using pdfplumber and ReportLab canvas.
    """
    trans_dir = os.path.join("uploads", "translated")
    if not os.path.exists(trans_dir):
        os.makedirs(trans_dir, exist_ok=True)
    
    final_output_path = os.path.join(trans_dir, os.path.basename(output_path))
    translator = Translator()

    # Font Setup
    font_path = r"C:\Windows\Fonts\nirmala.ttf"
    font_name = "Helvetica"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Nirmala', font_path))
            font_name = 'Nirmala'
        except: pass

    # 1. Start PDF Generation
    c = canvas.Canvas(final_output_path, pagesize=letter)
    text_found = False

    try:
        with pdfplumber.open(input_path) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                p_width = float(page.width)
                p_height = float(page.height)
                c.setPageSize((p_width, p_height))

                # Extract words with layout info
                words = page.extract_words()
                if not words:
                    continue
                
                text_found = True
                # Group words into lines based on vertical proximity (top)
                lines = {}
                for w in words:
                    y = round(w['top'], 1)
                    if y not in lines: lines[y] = []
                    lines[y].append(w)
                
                # Sort and process lines
                for y_top in sorted(lines.keys()):
                    line_words = sorted(lines[y_top], key=lambda x: x['x0'])
                    orig_text = " ".join([w['text'] for w in line_words])
                    
                    # Coordinates
                    x0 = line_words[0]['x0']
                    y0 = p_height - line_words[0]['bottom'] # Convert to bottom-left origin
                    w_max = line_words[-1]['x1'] - x0
                    
                    # Translate
                    try:
                        trans = translator.translate(orig_text, dest=target_lang).text
                    except:
                        trans = orig_text
                    
                    # Draw text
                    # Approximate font size based on bounding box
                    f_size = line_words[0].get('height', 10)
                    c.setFont(font_name, f_size)
                    
                    # Scale font if translated text is too wide
                    t_width = c.stringWidth(trans, font_name, f_size)
                    current_f_size = f_size
                    while t_width > w_max and current_f_size > 4:
                        current_f_size -= 0.5
                        c.setFont(font_name, current_f_size)
                        t_width = c.stringWidth(trans, font_name, current_f_size)
                    
                    c.drawString(x0, y0, trans)
                
                c.showPage()
    except Exception as e:
        print(f"Error in layout extraction: {str(e)}")

    # 2. OCR Fallback if no text was found via pdfplumber
    if not text_found:
        tess_path = get_tesseract_path()
        if tess_path:
            pytesseract.pytesseract.tesseract_cmd = tess_path
            try:
                images = convert_from_path(input_path, dpi=300)
                for img in images:
                    gray = ImageOps.grayscale(img)
                    proc = gray.point(lambda p: 255 if p > 150 else 0).convert('1')
                    
                    # Extract with layout data (HOCR or data blocks)
                    data = pytesseract.image_to_data(proc, output_type=pytesseract.Output.DICT)
                    
                    # Get page dimensions
                    img_w, img_h = proc.size
                    c.setPageSize((img_w * 72/300, img_h * 72/300)) # Scale to points
                    
                    for i in range(len(data['text'])):
                        if int(data['conf'][i]) > 30: # Only confident text
                            txt = data['text'][i].strip()
                            if txt:
                                try:
                                    txt_trans = translator.translate(txt, dest=target_lang).text
                                except: txt_trans = txt
                                
                                # Convert px to points
                                x = data['left'][i] * 72 / 300
                                y = (img_h - data['top'][i] - data['height'][i]) * 72 / 300
                                
                                c.setFont(font_name, data['height'][i] * 72 / 300 * 0.8)
                                c.drawString(x, y, txt_trans)
                    c.showPage()
                    text_found = True
            except: pass

    if not text_found:
        # Final emergency fallback: Create a simple message page
        c.setPageSize(letter)
        c.setFont("Helvetica", 12)
        c.drawString(1*inch, 10*inch, "Extraction failed. Document may be blank or corrupted.")
        c.showPage()

    c.save()
    return final_output_path
