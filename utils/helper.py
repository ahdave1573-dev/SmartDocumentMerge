"""
helper.py - Utility/helper functions for the Smart Document Merge System
"""

import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    Returns True if allowed, False otherwise.
    """
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    )


def get_file_extension(filename):
    """Return the lowercase file extension without the dot."""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def generate_unique_filename(original_filename):
    """
    Generate a unique filename using UUID to avoid collisions.
    Preserves the original file extension.
    """
    ext = get_file_extension(original_filename)
    safe_name = secure_filename(original_filename)
    base = safe_name.rsplit('.', 1)[0] if '.' in safe_name else safe_name
    unique_name = f"{base}_{uuid.uuid4().hex[:8]}.{ext}"
    return unique_name


def get_upload_path(filename):
    """Return the full absolute path for a file in the upload folder."""
    return os.path.join(Config.UPLOAD_FOLDER, filename)


def format_file_size(size_bytes):
    """
    Convert file size in bytes to a human-readable string.
    E.g., 1048576 -> '1.00 MB'
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def delete_file_if_exists(filepath):
    """
    Delete a file from disk if it exists.
    Returns True on success, False if the file didn't exist.
    """
    if os.path.exists(filepath):
        os.remove(filepath)
        return True
    return False


def get_pdf_name_from_stored(stored_name):
    """
    Given a stored filename (any extension), return the expected
    converted PDF filename.
    """
    base = stored_name.rsplit('.', 1)[0] if '.' in stored_name else stored_name
    return f"{base}_converted.pdf"
