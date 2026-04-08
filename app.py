"""
app.py — Smart PDF Tools (iLovePDF-like)
Main Flask application with routes for all 8 PDF tools.
"""
import os
import uuid
import zipfile

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

from config import Config
from models.db import init_db, log_operation, get_history
from utils.pdf_merge    import merge_pdfs
from utils.pdf_split    import split_pdf
from utils.word_to_pdf  import word_to_pdf
from utils.pdf_to_word  import pdf_to_word
from utils.image_to_pdf import images_to_pdf
from utils.pdf_to_image import pdf_to_images
from utils.pdf_secure   import secure_pdf, unlock_pdf

import json

# ── App Init ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

@app.template_filter('from_json')
def from_json_filter(s):
    return json.loads(s)

with app.app_context():
    init_db()

# ── Tool definitions (shared with templates) ─────────────────────────────────
TOOLS = [
    {
        'id': 'merge',
        'title': 'Merge PDF',
        'desc': 'Combine multiple PDF files into one document',
        'icon': '🔀',
        'color': '#e53e3e',
        'bg': 'linear-gradient(135deg,#f87171,#e53e3e)',
        'accept': '.pdf',
        'multiple': True,
    },
    {
        'id': 'split',
        'title': 'Split PDF',
        'desc': 'Split a PDF into separate pages or page ranges',
        'icon': '✂️',
        'color': '#f97316',
        'bg': 'linear-gradient(135deg,#fb923c,#ea580c)',
        'accept': '.pdf',
        'multiple': False,
    },
    {
        'id': 'word-to-pdf',
        'title': 'Word to PDF',
        'desc': 'Convert DOC/DOCX files to PDF format',
        'icon': '📝',
        'color': '#3b82f6',
        'bg': 'linear-gradient(135deg,#60a5fa,#2563eb)',
        'accept': '.doc,.docx',
        'multiple': False,
    },
    {
        'id': 'pdf-to-word',
        'title': 'PDF to Word',
        'desc': 'Extract text from PDF into a Word document',
        'icon': '📄',
        'color': '#06b6d4',
        'bg': 'linear-gradient(135deg,#22d3ee,#0891b2)',
        'accept': '.pdf',
        'multiple': False,
    },
    {
        'id': 'image-to-pdf',
        'title': 'Image to PDF',
        'desc': 'Convert JPG/PNG images into a single PDF',
        'icon': '🖼️',
        'color': '#22c55e',
        'bg': 'linear-gradient(135deg,#4ade80,#16a34a)',
        'accept': '.jpg,.jpeg,.png,.bmp,.gif,.webp',
        'multiple': True,
    },
    {
        'id': 'pdf-to-image',
        'title': 'PDF to Image',
        'desc': 'Convert PDF pages into JPG or PNG images',
        'icon': '🎨',
        'color': '#ec4899',
        'bg': 'linear-gradient(135deg,#f472b6,#db2777)',
        'accept': '.pdf',
        'multiple': False,
    },
    {
        'id': 'secure',
        'title': 'Secure PDF',
        'desc': 'Password protect or unlock PDF files',
        'icon': '🔒',
        'color': '#f59e0b',
        'bg': 'linear-gradient(135deg,#fbbf24,#d97706)',
        'accept': '.pdf',
        'multiple': False,
    },
]

TOOL_MAP = {t['id']: t for t in TOOLS}

# ── Helpers ───────────────────────────────────────────────────────────────────

def allowed_file(filename, tool_id):
    """Check if filename extension matches the tool's accepted types."""
    tool = TOOL_MAP.get(tool_id)
    if not tool or '.' not in filename:
        return False
    ext = '.' + filename.rsplit('.', 1)[-1].lower()
    allowed = [e.strip().lower() for e in tool['accept'].split(',')]
    return ext in allowed


def save_upload(file):
    """Save one uploaded file with a UUID filename. Returns (stored_name, full_path)."""
    original = secure_filename(file.filename)
    ext = original.rsplit('.', 1)[-1].lower() if '.' in original else 'bin'
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(Config.UPLOAD_FOLDER, stored)
    file.save(path)
    return stored, path

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    """Home page — tool grid."""
    return render_template('index.html', tools=TOOLS)


@app.route('/tool/<tool_id>')
def tool_page(tool_id):
    """Generic tool page — driven by tool config."""
    tool = TOOL_MAP.get(tool_id)
    if not tool:
        return render_template('index.html', tools=TOOLS), 404
    return render_template('tool.html', tool=tool, tools=TOOLS)


@app.route('/process/<tool_id>', methods=['POST'])
def process(tool_id):
    """
    AJAX endpoint — receives uploaded files + form data,
    runs the appropriate utility, returns JSON with download links.
    """
    tool = TOOL_MAP.get(tool_id)
    if not tool:
        return jsonify({'success': False, 'message': 'Unknown tool.'}), 404

    # ── Validate uploads ──
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'success': False, 'message': 'No files uploaded.'}), 400

    for f in files:
        if not allowed_file(f.filename, tool_id):
            return jsonify({
                'success': False,
                'message': f'"{f.filename}" is not supported. Accepted: {tool["accept"]}'
            }), 400

    # ── Save uploads ──
    saved, input_paths = [], []
    try:
        for f in files:
            stored, path = save_upload(f)
            saved.append({'original': f.filename, 'stored': stored, 'path': path})
            input_paths.append(path)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload error: {e}'}), 500

    # ── Process ──
    out_dir    = Config.UPLOAD_FOLDER
    extra      = request.form
    
    # Custom Name Handling
    custom_name = extra.get('custom_name', '').strip()
    if custom_name:
        # Secure the name and ensure it doesn't have multiple extensions
        custom_name = secure_filename(custom_name).rsplit('.', 1)[0]
        out_prefix = f"{custom_name}_{uuid.uuid4().hex[:5]}" # Add small unique suffix to avoid collisions
    else:
        out_prefix = uuid.uuid4().hex[:10]
        
    downloads  = []

    try:
        # ---- Merge ----
        if tool_id == 'merge':
            out_file = os.path.join(out_dir, out_prefix + '_merged.pdf')
            merge_pdfs(input_paths, out_file)
            downloads = [{'name': os.path.basename(out_file),
                          'label': '⬇️ Download Merged PDF'}]

        # ---- Split ----
        elif tool_id == 'split':
            mode        = extra.get('split_mode', 'all')
            page_range  = extra.get('page_range', '').strip()
            results = split_pdf(input_paths[0], out_dir, mode, page_range, out_prefix)
            if len(results) == 1:
                downloads = [{'name': os.path.basename(results[0]),
                              'label': '⬇️ Download PDF'}]
            else:
                zip_name = out_prefix + '_pages.zip'
                zip_path = os.path.join(out_dir, zip_name)
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for r in results:
                        zf.write(r, os.path.basename(r))
                downloads = [{'name': zip_name,
                              'label': f'⬇️ Download All {len(results)} Pages (ZIP)'}]

        # ---- Word to PDF ----
        elif tool_id == 'word-to-pdf':
            out_file = os.path.join(out_dir, out_prefix + '.pdf')
            word_to_pdf(input_paths[0], out_file)
            downloads = [{'name': os.path.basename(out_file),
                          'label': '⬇️ Download PDF'}]

        # ---- PDF to Word ----
        elif tool_id == 'pdf-to-word':
            out_file = os.path.join(out_dir, out_prefix + '.docx')
            pdf_to_word(input_paths[0], out_file)
            downloads = [{'name': os.path.basename(out_file),
                          'label': '⬇️ Download Word Document'}]

        # ---- Image to PDF ----
        elif tool_id == 'image-to-pdf':
            out_file = os.path.join(out_dir, out_prefix + '.pdf')
            images_to_pdf(input_paths, out_file)
            downloads = [{'name': os.path.basename(out_file),
                          'label': '⬇️ Download PDF'}]

        # ---- PDF to Image ----
        elif tool_id == 'pdf-to-image':
            fmt     = extra.get('image_format', 'jpg').lower()
            results = pdf_to_images(input_paths[0], out_dir, out_prefix, fmt)
            if len(results) == 1:
                downloads = [{'name': os.path.basename(results[0]),
                              'label': '⬇️ Download Image'}]
            else:
                zip_name = out_prefix + '_images.zip'
                zip_path = os.path.join(out_dir, zip_name)
                with zipfile.ZipFile(zip_path, 'w') as zf:
                    for r in results:
                        zf.write(r, os.path.basename(r))
                downloads = [{'name': zip_name,
                              'label': f'⬇️ Download {len(results)} Images (ZIP)'}]

        # ---- Secure PDF ----
        elif tool_id == 'secure':
            action = extra.get('secure_action', 'protect')
            if action == 'protect':
                password = extra.get('password', '').strip()
                if not password:
                    return jsonify({'success': False,
                                    'message': 'Please enter a password to protect the PDF.'}), 400
                owner_pass = extra.get('owner_password', password).strip() or password
                out_file = os.path.join(out_dir, out_prefix + '_protected.pdf')
                secure_pdf(input_paths[0], out_file, password, owner_pass)
                downloads = [{'name': os.path.basename(out_file),
                              'label': '⬇️ Download Protected PDF'}]
            else:  # unlock
                unlock_pass = extra.get('unlock_password', '').strip()
                out_file    = os.path.join(out_dir, out_prefix + '_unlocked.pdf')
                result = unlock_pdf(input_paths[0], out_file, unlock_pass)
                if not result['success']:
                    return jsonify({'success': False, 'message': result['message']}), 400
                downloads = [{'name': os.path.basename(out_file),
                              'label': '⬇️ Download Unlocked PDF'}]

        else:
            return jsonify({'success': False, 'message': 'Tool not yet implemented.'}), 501

        # Log to DB
        log_operation(tool_id,
                      [s['original'] for s in saved],
                      [d['name'] for d in downloads])

        return jsonify({'success': True, 'downloads': downloads})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """
    Serves files from the uploads directory and its subdirectories.
    """
    directory = app.config['UPLOAD_FOLDER']
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/history')
def history():
    """Recent operations page."""
    ops = get_history(50)
    return render_template('history.html', ops=ops, tools=TOOLS)


# ── Error Handlers ────────────────────────────────────────────────────────────
@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False,
                    'message': 'File too large. Maximum allowed is 100 MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html', tools=TOOLS), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'message': 'Internal server error.'}), 500

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
