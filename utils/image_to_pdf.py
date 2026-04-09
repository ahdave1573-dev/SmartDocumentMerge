"""utils/image_to_pdf.py — Convert one or more images into a single PDF"""
import os
from PIL import Image


def images_to_pdf(input_paths: list[str], output_path: str) -> str:
    """
    Convert a list of image files (JPG, PNG, BMP, etc.) into a single PDF.
    Each image becomes one page. Portrait/landscape is auto-detected.

    Returns output_path on success.
    """
    if not input_paths:
        raise ValueError('No image files provided.')

    images = []
    for path in input_paths:
        img = Image.open(path)
        # Convert to RGB (PDF doesn't support RGBA or palette-mode directly)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)

    if not images:
        raise ValueError('No valid images could be loaded.')

    # First image is the base; append the rest
    first = images[0]
    rest  = images[1:]

    first.save(
        output_path,
        format='PDF',
        save_all=True,
        append_images=rest,
        resolution=150,   # DPI for the PDF
    )

    # Close all images
    for img in images:
        img.close()

    return output_path
