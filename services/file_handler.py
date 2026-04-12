"""
file_handler.py - Handles file uploads, validation, and storage
"""

import os
from flask import request
from werkzeug.utils import secure_filename
from config import Config
from utils.helper import allowed_file, generate_unique_filename, get_upload_path
from models.document_model import insert_document


def handle_upload(file):
    """
    Validate and save an uploaded file.
    Returns a dict with success status, message, and file info.
    """
    # Check if filename is present
    if not file or file.filename == '':
        return {'success': False, 'message': 'No file selected.'}

    original_name = file.filename

    # Validate file extension
    if not allowed_file(original_name):
        return {
            'success': False,
            'message': f'File "{original_name}" has an unsupported format. '
                       f'Only PDF, DOCX, and TXT files are allowed.'
        }

    # Generate unique stored filename to prevent overwrites
    stored_name = generate_unique_filename(original_name)
    save_path = get_upload_path(stored_name)

    try:
        # Save the file to the uploads directory
        file.save(save_path)

        # Get actual file size
        size = os.path.getsize(save_path)

        # Get file extension
        ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''

        # Record in database
        doc_id = insert_document(original_name, stored_name, ext, size)

        return {
            'success': True,
            'message': f'File "{original_name}" uploaded successfully.',
            'doc_id': doc_id,
            'original_name': original_name,
            'stored_name': stored_name,
            'file_type': ext,
            'size': size
        }

    except Exception as e:
        # Clean up partially saved file if error occurred
        if os.path.exists(save_path):
            os.remove(save_path)
        return {
            'success': False,
            'message': f'Failed to save "{original_name}": {str(e)}'
        }


def handle_multiple_uploads(files):
    """
    Process a list of uploaded files.
    Returns a list of result dicts, one per file.
    """
    results = []
    for file in files:
        result = handle_upload(file)
        results.append(result)
    return results
