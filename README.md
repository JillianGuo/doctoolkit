# Document Processing Toolkit

A web-based document processing utility built with Python and Streamlit. Merge, split, rotate, and convert PDFs and images with high-quality output. Designed for local network (LAN) deployment.

---

## Features

### 📎 Document Merging
- **Merge PDFs and images** into a single PDF with automatic table of contents
- **High-quality image processing** with 300 DPI target resolution
- **Smart scaling** preserves aspect ratios and image sharpness
- **Supports formats**: PDF, JPG, JPEG, PNG

### ✂️ PDF Splitting
- **Split by page ranges** with custom output filenames
- **Batch processing** with ZIP archive download
- **Flexible syntax**: Single pages (e.g., "5") or ranges (e.g., "1-3")

### 🖼️ Image to PDF Conversion
- **Letter-size PDF output** (8.5" × 11") at 300 DPI
- **Preserves image quality** with optimal scaling
- **Supports**: JPG, JPEG, PNG formats

### 🌀 PDF Rotation
- **Rotate pages** by 90°, 180°, or 270°
- **Clockwise or counterclockwise** rotation options
- **Batch processing** for all pages

---

## Project Structure

```
doctoolkit/
├── app.py              # Streamlit web interface
├── doc_processor.py    # Document processing logic
├── requirements.txt    # Python dependencies
├── Dockerfile         # Container deployment
└── README.md         # Documentation
```

---

## Installation & Usage

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Docker Deployment
```bash
# Build image
docker build -t pdf-toolkit .

# Run container
docker run -p 8501:8501 pdf-toolkit
```

Access the application at `http://localhost:8501`

---

## Dependencies

- **Streamlit**: Web interface framework
- **PyMuPDF (fitz)**: PDF manipulation and processing
- **Pillow (PIL)**: High-quality image processing
- **Python 3.13+**: Runtime environment

---

## License

MIT License. Free to use and modify.