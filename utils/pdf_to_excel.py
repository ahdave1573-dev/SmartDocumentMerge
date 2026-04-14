"""utils/pdf_to_excel.py — Refined PDF Table Extraction with Camelot, Tabula, pdfplumber, and OCR"""
import os
import io
import pandas as pd
import pdfplumber
import tabula
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

try:
    import camelot
except ImportError:
    camelot = None

# Helper to find tesseract
def get_tesseract_path():
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Himansubhai\AppData\Local\Tesseract-OCR\tesseract.exe",
        r"C:\Users\Anshul\AppData\Local\Tesseract-OCR\tesseract.exe",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None

def pdf_to_excel(input_path: str, output_path: str) -> str:
    """
    Extract tables from PDF using multiple methods:
    1. Camelot (Lattice & Stream)
    2. Tabula-py
    3. pdfplumber (Standard & Borderless)
    4. OCR Fallback (pytesseract)
    5. Text-to-Excel Fallback
    Outputs each table to a separate sheet in Excel.
    """
    all_dfs = []
    
    # --- Method 1: Camelot (Strongest for structured tables) ---
    if camelot:
        try:
            # Try Lattice (for tables with lines)
            tables = camelot.read_pdf(input_path, pages='all', flavor='lattice')
            for i, table in enumerate(tables):
                df = table.df
                if not df.empty:
                    df['Method'] = 'Camelot-Lattice'
                    all_dfs.append(df)
            
            # Try Stream (for tables without lines)
            tables_stream = camelot.read_pdf(input_path, pages='all', flavor='stream')
            for i, table in enumerate(tables_stream):
                df = table.df
                if not df.empty:
                    # Check if we already have this data (rough duplicate check)
                    if not any(df.equals(existing.iloc[:, :-1]) for existing in all_dfs if 'Camelot' in str(existing.get('Method'))):
                        df['Method'] = 'Camelot-Stream'
                        all_dfs.append(df)
        except Exception as e:
            print(f"Camelot failed: {e}")

    # --- Method 2: Tabula-py (Fast and reliable) ---
    if not all_dfs:
        try:
            tabs = tabula.read_pdf(input_path, pages='all', multiple_tables=True, silent=True)
            if tabs:
                for i, df in enumerate(tabs):
                    if not df.empty:
                        df['Method'] = 'Tabula'
                        all_dfs.append(df)
        except Exception as e:
            print(f"Tabula failed: {e}")

    # --- Method 3: pdfplumber (Page-by-page control) ---
    with pdfplumber.open(input_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_found = False
            
            # Standard extraction
            extracted = page.extract_tables()
            if not extracted:
                # Borderless extraction
                extracted = page.extract_tables(table_settings={
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_y_tolerance": 3,
                })
            
            if extracted:
                for table in extracted:
                    if table:
                        clean = [[str(col).strip() if col is not None else "" for col in row] for row in table]
                        if any(any(col for col in row) for row in clean):
                            df = pd.DataFrame(clean)
                            df['Page'] = i + 1
                            df['Method'] = 'pdfplumber'
                            # Only add if we don't have similar data already
                            all_dfs.append(df)
                            page_found = True

            # --- Method 4: OCR Fallback for scanned/image pages ---
            if not page_found:
                text = page.extract_text() or ""
                if len(text.strip()) < 20: # Threshold for "likely scanned"
                    tess_path = get_tesseract_path()
                    if tess_path:
                        pytesseract.pytesseract.tesseract_cmd = tess_path
                        try:
                            images = convert_from_path(input_path, first_page=i+1, last_page=i+1, dpi=300)
                            for img in images:
                                ocr_text = pytesseract.image_to_string(img)
                                if ocr_text.strip():
                                    rows = [line.split('  ') for line in ocr_text.split('\n') if line.strip()]
                                    if rows:
                                        df = pd.DataFrame(rows)
                                        df['Page'] = i + 1
                                        df['Method'] = 'OCR'
                                        all_dfs.append(df)
                                        page_found = True
                        except Exception as e:
                            print(f"OCR failed for page {i+1}: {e}")

            # --- Method 5: Final Text-to-Excel Fallback ---
            if not page_found:
                text = page.extract_text()
                if text and text.strip():
                    lines = [[line.strip()] for line in text.split('\n') if line.strip()]
                    df = pd.DataFrame(lines, columns=["Extracted Text"])
                    df['Page'] = i + 1
                    df['Method'] = 'Text Fallback'
                    all_dfs.append(df)

    # Export to Excel
    if all_dfs:
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                for idx, df in enumerate(all_dfs):
                    sheet_name = f"Table_{idx+1}"
                    if 'Page' in df.columns:
                        p = df['Page'].iloc[0] if not df.empty else idx+1
                        sheet_name = f"Page_{p}_T{idx+1}"
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        except Exception as e:
            # Final fallback to single sheet if multi-sheet fails
            pd.concat(all_dfs, ignore_index=True, sort=False).to_excel(output_path, index=False)
    else:
        # Emergency backup: even if all failed, write a message in a row
        pd.DataFrame([["No data could be extracted from this PDF."]]).to_excel(output_path, index=False)

    return output_path
