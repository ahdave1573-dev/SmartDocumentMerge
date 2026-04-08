"""config.py — App configuration for Smart PDF Tools"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'smartpdf-secret-key-2024'
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

    # Allowed extensions per tool
    ALLOWED_PDF       = {'pdf'}
    ALLOWED_WORD      = {'doc', 'docx'}
    ALLOWED_IMAGE     = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'tiff'}

    DATABASE = os.path.join(BASE_DIR, 'database.db')
    DEBUG = True

# Ensure uploads folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
