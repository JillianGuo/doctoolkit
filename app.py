import streamlit as st
from io import BytesIO
import os
from doc_processor import merge_docs, convert_image_to_pdf, split_pdf, create_zip_archive, rotate_pdf


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
def merge_docs_ui():
    st.subheader("🔗 Merge Documents (PDF and/or images)")
    uploaded_files = st.file_uploader(
        "Upload PDF files and images", type=["pdf", "jpg", "jpeg", "png"], accept_multiple_files=True
    )

    client_name = st.text_input("Client Name (optional):").strip()
    default_filename = f"T1_Docs_{client_name}_2024.pdf" if client_name else "T1_Docs_2024.pdf"
    custom_filename = st.text_input("Output File Name:", value=default_filename)

    if uploaded_files and len(uploaded_files) >= 1:
        if st.button("Merge PDFs"):
            try:
                output_bytes = merge_docs(uploaded_files)

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
        st.info("Please upload at least one PDF file or image to merge.")


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
            buffer = convert_image_to_pdf(uploaded_image)

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
            # Parse split ranges
            split_ranges = []
            for line in split_input.strip().splitlines():
                if ':' not in line:
                    st.warning(f"Skipping malformed line: {line}")
                    continue
                range_part, filename = map(str.strip, line.split(":", 1))
                split_ranges.append((range_part, filename))
            
            split_results = split_pdf(uploaded_file, split_ranges)
            st.success("PDF split completed!")

            # ✅ Display list of output files
            st.markdown("**Generated Files:**")
            for filename, _ in split_results:
                st.markdown(f"📄 {filename}")

            # ✅ Create ZIP archive in memory
            zip_buffer = create_zip_archive(split_results)

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
            direction_str = "right" if direction == "↻ Rotate Right" else "left"
            buffer, rotated_pages = rotate_pdf(uploaded_file, degrees, direction_str)

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
    merge_docs_ui()
elif feature == "Convert Image to PDF":
    convert_images_ui()
elif feature == "Split PDF":
    split_pdf_ui()
elif feature == "Rotate PDF":
    rotate_pdf_ui()