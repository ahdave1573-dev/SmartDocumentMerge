# 🚀 Smart Document Merge

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A powerful, modern, and easy-to-use web-based PDF utility tool**

[Features](#-features) • [Installation](#-getting-started) • [Usage](#-usage) • [Tech Stack](#️-tech-stack) • [License](#-license)

</div>

---

## 📖 About

**Smart Document Merge** is a comprehensive web-based document processing platform built with Python and Flask. Similar to iLovePDF, it provides a suite of powerful tools to manage PDF documents, images, and Word files directly from your browser—no software installation required!

Whether you need to merge multiple PDFs, convert documents between formats, or secure your files with encryption, Smart Document Merge has you covered.

## ✨ Features

### 📄 PDF Operations
- **🔀 Merge PDF**: Combine multiple PDF files into a single document
- **✂️ Split PDF**: Extract specific pages or split all pages into separate files
- **🔒 Protect PDF**: Add password encryption to secure your documents
- **🔓 Unlock PDF**: Remove password protection (requires valid password)

### 🔄 Document Conversion
- **📝 Word to PDF**: Convert `.docx` and `.doc` files into high-quality PDFs
- **📄 PDF to Word**: Extract text from PDFs and save as editable Word documents
- **🖼️ Image to PDF**: Convert images (JPG, PNG, BMP, etc.) into PDF format
- **🎨 PDF to Image**: Render PDF pages as JPG or PNG images

### 📊 Additional Features
- **📂 Operation History**: Track and review your recent file processing activities
- **🚀 Fast Processing**: Optimized for quick document handling
- **💾 Temporary Storage**: Secure file handling with automatic cleanup

## 🛠️ Tech Stack

| Category | Technologies |
|----------|-------------|
| **Backend** | Python, Flask |
| **Database** | SQLite |
| **PDF Processing** | pypdf, PyMuPDF (fitz) |
| **Document Handling** | python-docx, reportlab |
| **Image Processing** | Pillow (PIL) |

### Key Libraries
- `pypdf` - PDF manipulation and merging
- `python-docx` - Word document processing
- `reportlab` - PDF generation from scratch
- `Pillow` - Image processing and conversion
- `PyMuPDF` - High-quality PDF rendering

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- **Python 3.8 or higher** installed
- **pip** package manager
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahdave1573-dev/SmartDocumentMerge.git
   cd SmartDocumentMerge
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

**Option 1: Python Command**
```bash
python app.py
```

**Option 2: Windows Batch File**
```bash
run.bat
```

The application will start on `http://127.0.0.1:5000`

🌐 Open your browser and navigate to the URL to start using Smart Document Merge!

## 📂 Project Structure

```
SmartDocumentMerge/
│
├── app.py                  # Main Flask application & routes
├── config.py               # Configuration settings
├── database.db             # SQLite database (auto-generated)
├── requirements.txt        # Python dependencies
├── run.bat                 # Windows startup script
│
├── models/                 # Database models
│   └── history.py          # Operation history model
│
├── services/               # Business logic layer
│   ├── pdf_service.py      # PDF operations
│   ├── image_service.py    # Image operations
│   └── word_service.py     # Word operations
│
├── static/                 # Frontend assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── images/            # Icons and images
│
├── templates/              # HTML templates (Jinja2)
│   ├── base.html          # Base template
│   ├── index.html         # Homepage
│   └── history.html       # Operation history page
│
├── uploads/                # Temporary file storage
│   └── .gitkeep           # Keep directory in git
│
└── utils/                  # Utility functions
    ├── pdf_utils.py       # PDF helper functions
    ├── image_utils.py     # Image helper functions
    └── word_utils.py      # Word helper functions
```

## 💡 Usage

### Merge PDF Files
1. Navigate to the **Merge PDF** section
2. Upload multiple PDF files (drag & drop or click to browse)
3. Arrange files in desired order
4. Click **Merge** to combine into a single PDF
5. Download the merged document

### Convert Word to PDF
1. Go to **Word to PDF** section
2. Upload your `.docx` or `.doc` file
3. Click **Convert**
4. Download the generated PDF

### Secure a PDF
1. Select **Protect PDF**
2. Upload your PDF file
3. Enter a password
4. Click **Protect** to encrypt the document

## 🔐 Security & Privacy

- All file processing happens **locally** on the server
- Uploaded files are **automatically deleted** after processing
- Password-protected PDFs use **strong encryption**
- No files are stored permanently or shared with third parties

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📋 Roadmap

- [ ] Add OCR support for scanned PDFs
- [ ] Implement batch processing
- [ ] Add PDF compression feature
- [ ] Support for more image formats
- [ ] Dark mode UI
- [ ] API endpoints for programmatic access

## 🐛 Known Issues

- Large PDF files (>50MB) may take longer to process
- Some complex Word documents may lose formatting during conversion

## 📝 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Anshul Dave**
- GitHub: [@ahdave1573-dev](https://github.com/ahdave1573-dev)
- Email: ahdave1573@gmail.com
- Project: [SmartDocumentMerge](https://github.com/ahdave1573-dev/SmartDocumentMerge)

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [pypdf](https://github.com/py-pdf/pypdf) - PDF library
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF rendering
- Icons from [FontAwesome](https://fontawesome.com/)

---

<div align="center">

**Made with ❤️ using Python and Flask**

⭐ Star this repo if you find it helpful!

</div>
