import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import os
import zipfile


st.set_page_config(page_title="PDF Toolkit", layout="centered")
st.title("📎 PDF Toolkit")

# Sidebar feature selection
feature = st.sidebar.selectbox("Choose a Feature", [
    "Merge PDFs",
    "Convert Image to PDF",
    "Split PDF", 
    "Rotate PDF"
])


# ------------------------------
# Feature 1: Merge PDFs
# ------------------------------
def merge_pdfs_ui():
    st.subheader("🔗 Merge PDF Files")
    uploaded_files = st.file_uploader(
        "Upload PDF files", type="pdf", accept_multiple_files=True
    )

    client_name = st.text_input("Client Name (optional):").strip()
    default_filename = f"T1_Docs_{client_name}_2024.pdf" if client_name else "T1_Docs_2024.pdf"
    custom_filename = st.text_input("Output File Name:", value=default_filename)

    if uploaded_files and len(uploaded_files) > 1:
        if st.button("Merge PDFs"):
            try:
                merged_doc = fitz.open()
                toc = []
                current_page = 0

                for file in uploaded_files:
                    pdf = fitz.open(stream=file.read(), filetype="pdf")
                    merged_doc.insert_pdf(pdf)
                    toc.append([1, file.name, current_page + 1, 0])  # TOC entry: level, title, page number
                    current_page += pdf.page_count
                    pdf.close()

                merged_doc.set_toc(toc)
                output_bytes = merged_doc.write()
                merged_doc.close()

                st.success("PDFs merged successfully!")
                st.download_button(
                    "⬇️ Download", 
                    BytesIO(output_bytes), 
                    custom_filename, 
                    mime="application/pdf"
                )

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Please upload at least two PDF files to merge.")


# ------------------------------
# Feature 2: Convert Images to PDF
# ------------------------------
def convert_images_ui():
    st.subheader("🖼 Convert Image to Letter-Size PDF (300 DPI Sharp Fit)")

    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    # US Letter size in points (8.5 × 11 inches at 72 DPI)
    PAGE_WIDTH, PAGE_HEIGHT = 612, 792

    if uploaded_image:
        base_name = os.path.splitext(uploaded_image.name)[0]
        default_filename = f"{base_name}.pdf"

        output_name_input = st.text_input(
            "Output PDF Filename:",
            value=default_filename,
            help="Customize the output filename ('.pdf' will be added if not included)."
        )

    if uploaded_image and st.button("Convert"):
        try:
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

            # Ensure output name ends with .pdf
            output_name = output_name_input if output_name_input.lower().endswith(".pdf") else f"{output_name_input}.pdf"

            st.success("Image converted to PDF.")
            st.download_button(
                label=f"⬇️ Download",
                data=buffer,
                file_name=output_name,
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.info("Upload an image to begin conversion.")

# ------------------------------
# Feature 3: Split PDF by Page Ranges
# ------------------------------
def split_pdf_ui():
    st.subheader("✂️ Split PDF")

    uploaded_file = st.file_uploader("Upload a PDF to split", type="pdf")

    st.markdown("Enter the page ranges **and output file names**, one per line:")

    split_input = st.text_area(
        label="Page Ranges and File Names",
        placeholder="1-3: Part1.pdf\n4-5: Part2.pdf\n6: CoverPage.pdf",
        help="Each line must have a page range, a colon, and the output file name."
    )

    if uploaded_file and split_input and st.button("Split PDF"):
        try:
            input_pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            split_results = []

            for line in split_input.strip().splitlines():
                if ':' not in line:
                    st.warning(f"Skipping malformed line: {line}")
                    continue

                range_part, filename = map(str.strip, line.split(":", 1))

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
            st.success("PDF split completed!")

            # ✅ Display list of output files
            st.markdown("**Generated Files:**")
            for filename, _ in split_results:
                st.markdown(f"📄 {filename}")

            # ✅ Create ZIP archive in memory
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for filename, buffer in split_results:
                    zipf.writestr(filename, buffer.read())

            zip_buffer.seek(0)

            st.download_button(
                label="⬇️ Download All as ZIP",
                data=zip_buffer,
                file_name="split_pdfs.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Error splitting PDF: {e}")
    else:
        st.info("Upload a PDF and enter valid ranges with filenames.")


# ------------------------------
# Feature 4: Rotate PDF Pages to Upright Orientation
# ------------------------------
def rotate_pdf_ui():
    st.subheader("🌀 Rotate PDF Pages")

    uploaded_file = st.file_uploader("Upload a PDF to rotate", type="pdf")

    degrees = st.selectbox("Rotate by degrees", [90, 180, 270])
    direction = st.radio("Rotation Direction", ["↻ Rotate Right", "↺ Rotate Left"])

    if uploaded_file:
        # Suggest a default output name based on input file and settings
        base_name = os.path.splitext(uploaded_file.name)[0]
        direction_label = "right" if direction == "↻ Rotate Right" else "left"
        suggested_filename = f"{base_name}_rotated.pdf"

        custom_filename = st.text_input(
            "Output PDF Filename:",
            value=suggested_filename,
            help="You can modify the name ('.pdf' will be added if missing)."
        )

    if uploaded_file and st.button("Rotate PDF"):
        try:
            pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            rotated_pages = 0

            for page in pdf:
                angle = degrees if direction == "↻ Rotate Right" else -degrees
                page.set_rotation((page.rotation + angle) % 360)
                rotated_pages += 1

            buffer = BytesIO()
            pdf.save(buffer)
            buffer.seek(0)
            pdf.close()

            # Ensure .pdf extension
            output_name = custom_filename if custom_filename.lower().endswith(".pdf") else f"{custom_filename}.pdf"

            st.success(f"{rotated_pages} page(s) rotated {direction.lower()}.")
            st.download_button(
                label=f"⬇️ Download",
                data=buffer,
                file_name=output_name,
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"Error processing PDF: {e}")
    elif not uploaded_file:
        st.info("Upload a PDF to begin.")


# ------------------------------
# Run selected feature
# ------------------------------
if feature == "Merge PDFs":
    merge_pdfs_ui()
elif feature == "Convert Image to PDF":
    convert_images_ui()
elif feature == "Split PDF":
    split_pdf_ui()
elif feature == "Rotate PDF":
    rotate_pdf_ui()