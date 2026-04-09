import os
import uuid
import io
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def pix_to_jpeg_bytes(pix, quality):
    """Encodes Pixmap to JPEG bytes with quality using Pillow if possible."""
    # Ensure RGB (JPEG doesn't support alpha)
    if pix.colorspace and (pix.colorspace.n > 3 or pix.alpha):
        pix = fitz.Pixmap(fitz.csRGB, pix)
    
    if HAS_PIL:
        try:
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            return buf.getvalue()
        except: pass
        
    # Fallback to internal if PIL fails
    return pix.tobytes("jpg")


def compress_pdf(input_path: str, output_path: str, comp_level: str = "basic") -> str:
    """
    Advanced PDF compression with two levels:
    - Basic: Standard image downsampling and structural cleanup.
    - Extreme: Rebuilds document and uses aggressive image shrinking.
    """
    if not FITZ_AVAILABLE:
        # Fallback to structural-only compression if PyMuPDF is not installed
        from pypdf import PdfWriter, PdfReader
        reader = PdfReader(input_path)
        writer = PdfWriter()
        for page in reader.pages:
            new_page = writer.add_page(page)
            new_page.compress_content_streams()
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)
        with open(output_path, 'wb') as f:
            writer.write(f)
        return output_path

    # Open original document
    src = fitz.open(input_path)
    
    # ── Level-Specific Settings ──
    if comp_level == "nuclear":
        # Nuclear Mode: Rasterize every page to an image
        doc = fitz.open() # Create new PDF
        for page in src:
            # 72 DPI and Quality 20 for absolute minimum size
            pix = page.get_pixmap(dpi=72) 
            img_data = pix_to_jpeg_bytes(pix, quality=20)
            new_page = doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=img_data)
            pix = None
        src.close()
    else:
        # Standard or Extreme: Object-level optimization
        if comp_level == "extreme":
            max_dim = 800      # Even smaller for extreme
            quality = 20       # Lower quality for extreme
            rebuild = True     # Rebuild structure
        else:
            max_dim = 1200     # Balanced
            quality = 40       # Standard high quality
            rebuild = False    # Standard save
            
        if rebuild:
            doc = fitz.open()  # New empty document
            doc.insert_pdf(src)
            src.close()
        else:
            doc = src

        # Track processed images
        processed_xrefs = set()
        
        # Iterate through all pages to find images
        for page in doc:
            img_list = page.get_images(full=True)
            for img in img_list:
                xref = img[0]
                if xref in processed_xrefs: continue
                processed_xrefs.add(xref)
                
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.width > max_dim or pix.height > max_dim:
                        shrink_factor = max(pix.width, pix.height) // max_dim
                        if shrink_factor >= 2: pix.shrink(shrink_factor)

                    new_img_data = pix_to_jpeg_bytes(pix, quality=quality)
                    
                    doc.replace_image(xref, stream=new_img_data)
                    pix = None 
                except: continue

        # Final Scrubbing
        if hasattr(doc, "scrub"):
            try:
                doc.scrub(javascript=True, metadata=True, thumbnails=True, embedded_files=True, attachments=True, form_fields=True, annotations=True)
            except: pass

    # Save with maximum structural optimization
    doc.save(
        output_path,
        garbage=4, deflate=True, clean=True, pretty=False, ascii=False, linear=False
    )
    doc.close()

    return output_path
