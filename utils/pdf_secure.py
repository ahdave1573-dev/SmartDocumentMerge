"""utils/pdf_secure.py — Password-protect or unlock PDF files using pypdf"""
from pypdf import PdfWriter, PdfReader
from pypdf.errors import FileNotDecryptedError


def secure_pdf(input_path: str, output_path: str,
               user_password: str, owner_password: str = None) -> str:
    """
    Encrypt a PDF with a user password (required to open)
    and an optional owner password (required to edit/print).

    Uses 128-bit RC4 encryption (compatible with all PDF readers).
    Returns output_path on success.
    """
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    # Encrypt: user_password to open, owner_password to modify
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password or user_password,
        use_128bit=True
    )

    with open(output_path, 'wb') as f:
        writer.write(f)

    return output_path


def unlock_pdf(input_path: str, output_path: str,
               password: str) -> dict:
    """
    Attempt to decrypt a password-protected PDF.

    Returns:
        {'success': True, 'path': output_path}
        {'success': False, 'message': reason}
    """
    reader = PdfReader(input_path)

    if not reader.is_encrypted:
        # File isn't encrypted — just copy it through
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(output_path, 'wb') as f:
            writer.write(f)
        return {'success': True, 'path': output_path,
                'message': 'File was not encrypted; copied as-is.'}

    try:
        result = reader.decrypt(password)
        if result == 0:
            return {'success': False,
                    'message': 'Incorrect password. Could not unlock the PDF.'}
    except (FileNotDecryptedError, Exception) as e:
        return {'success': False,
                'message': f'Decryption failed: {str(e)}'}

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(reader.metadata)

    with open(output_path, 'wb') as f:
        writer.write(f)

    return {'success': True, 'path': output_path}
