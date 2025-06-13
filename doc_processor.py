import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import zipfile


def merge_docs(uploaded_files):
    """
    Merge multiple PDF files and images into one PDF with table of contents.
    
    Args:
        uploaded_files: List of uploaded file objects (PDFs and images)
        
    Returns:
        bytes: Merged PDF as bytes
        
    Raises:
        Exception: If merge operation fails
    """
    merged_doc = fitz.open()
    toc = []
    current_page = 0
    
    # US Letter size in points (8.5 × 11 inches at 72 DPI)
    PAGE_WIDTH, PAGE_HEIGHT = 612, 792

    for file in uploaded_files:
        file_extension = file.name.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            # Handle PDF files
            pdf = fitz.open(stream=file.read(), filetype="pdf")
            merged_doc.insert_pdf(pdf)
            toc.append([1, file.name, current_page + 1, 0])  # TOC entry: level, title, page number
            current_page += pdf.page_count
            pdf.close()
        elif file_extension in ['jpg', 'jpeg', 'png']:
            # Handle image files with high sharpness preservation
            img = Image.open(file)
            
            # Preserve original image quality and convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert("RGB")
            
            width_px, height_px = img.size
            
            # Calculate target DPI for high quality (aim for 300 DPI)
            target_dpi = 300
            
            # Calculate the maximum dimensions that fit on the page at 300 DPI
            # 8.5 x 11 inches at 300 DPI = 2550 x 3300 pixels
            max_width_300dpi = int(8.5 * target_dpi)
            max_height_300dpi = int(11 * target_dpi)
            
            # Calculate scale to fit within page while maintaining high DPI
            scale_for_fit = min(max_width_300dpi / width_px, max_height_300dpi / height_px)
            
            # If image is larger than 300 DPI target, resize it for optimal quality
            if scale_for_fit < 1:
                new_width = int(width_px * scale_for_fit)
                new_height = int(height_px * scale_for_fit)
                # Use LANCZOS for high-quality resampling
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                width_px, height_px = new_width, new_height
            
            # Save as high-quality PNG with maximum compression but no quality loss
            img_buffer = BytesIO()
            img.save(img_buffer, format="PNG", optimize=True, compress_level=1)
            img_buffer.seek(0)

            # Create a new page in the merged document
            page = merged_doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)

            # Scale image to fit page while preserving aspect ratio
            # Convert pixel dimensions to points (72 DPI)
            scale = min(PAGE_WIDTH / width_px, PAGE_HEIGHT / height_px)
            draw_width = width_px * scale
            draw_height = height_px * scale
            x_offset = (PAGE_WIDTH - draw_width) / 2
            y_offset = (PAGE_HEIGHT - draw_height) / 2
            rect = fitz.Rect(x_offset, y_offset, x_offset + draw_width, y_offset + draw_height)

            # Insert image with high quality settings
            page.insert_image(rect, stream=img_buffer.getvalue(), keep_proportion=True)
            
            toc.append([1, file.name, current_page + 1, 0])  # TOC entry: level, title, page number
            current_page += 1

    merged_doc.set_toc(toc)
    output_bytes = merged_doc.write()
    merged_doc.close()
    
    return output_bytes


def convert_image_to_pdf(uploaded_image):
    """
    Convert an image to letter-size PDF with 300 DPI sharp fit.
    
    Args:
        uploaded_image: Uploaded image file object
        
    Returns:
        BytesIO: PDF buffer
        
    Raises:
        Exception: If conversion fails
    """
    # US Letter size in points (8.5 × 11 inches at 72 DPI)
    PAGE_WIDTH, PAGE_HEIGHT = 612, 792
    
    img = Image.open(uploaded_image).convert("RGB")
    width_px, height_px = img.size

    # Convert to PNG bytes for PyMuPDF
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    # Create a Letter-size PDF
    pdf = fitz.open()
    page = pdf.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)

    # Scale image to fit while preserving aspect ratio
    scale = min(PAGE_WIDTH / width_px, PAGE_HEIGHT / height_px)
    draw_width = width_px * scale
    draw_height = height_px * scale
    x_offset = (PAGE_WIDTH - draw_width) / 2
    y_offset = (PAGE_HEIGHT - draw_height) / 2
    rect = fitz.Rect(x_offset, y_offset, x_offset + draw_width, y_offset + draw_height)

    page.insert_image(rect, stream=img_buffer.getvalue())

    # Output to buffer
    buffer = BytesIO()
    pdf.save(buffer)
    buffer.seek(0)
    pdf.close()
    
    return buffer


def split_pdf(uploaded_file, split_ranges):
    """
    Split PDF by page ranges into multiple files.
    
    Args:
        uploaded_file: Uploaded PDF file object
        split_ranges: List of tuples (range_str, filename)
        
    Returns:
        list: List of tuples (filename, BytesIO buffer)
        
    Raises:
        Exception: If split operation fails
    """
    input_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    split_results = []

    for range_part, filename in split_ranges:
        if '-' in range_part:
            start, end = map(int, range_part.split('-'))
        else:
            start = int(range_part)
            end = start

        split_doc = fitz.open()
        split_doc.insert_pdf(input_pdf, from_page=start - 1, to_page=end - 1)

        buffer = BytesIO()
        split_doc.save(buffer)
        buffer.seek(0)
        split_doc.close()

        split_results.append((filename, buffer))

    input_pdf.close()
    return split_results


def create_zip_archive(split_results):
    """
    Create ZIP archive from split PDF results.
    
    Args:
        split_results: List of tuples (filename, buffer)
        
    Returns:
        BytesIO: ZIP archive buffer
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for filename, buffer in split_results:
            zipf.writestr(filename, buffer.read())
    
    zip_buffer.seek(0)
    return zip_buffer


def rotate_pdf(uploaded_file, degrees, direction):
    """
    Rotate PDF pages by specified degrees.
    
    Args:
        uploaded_file: Uploaded PDF file object
        degrees: Rotation degrees (90, 180, 270)
        direction: "right" or "left" rotation direction
        
    Returns:
        tuple: (BytesIO buffer, number of rotated pages)
        
    Raises:
        Exception: If rotation fails
    """
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    rotated_pages = 0

    for page in pdf:
        angle = degrees if direction == "right" else -degrees
        page.set_rotation((page.rotation + angle) % 360)
        rotated_pages += 1

    buffer = BytesIO()
    pdf.save(buffer)
    buffer.seek(0)
    pdf.close()
    
    return buffer, rotated_pages