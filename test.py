import io
import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,LETTER
from reportlab.lib.utils import ImageReader

def is_blank_page(pdf_page):
    """Check if a PDF page is blank by examining its text content."""
    text = pdf_page.get_text()
    return not text.strip()

def combine_pages(input_pdf_path, output_pdf_path, mini_pages_per_page):
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    num_groups = (total_pages + mini_pages_per_page - 1) // mini_pages_per_page  # Ceiling division

    temp_files = []

    page_width, page_height = A4

    # Determine the layout based on the number of mini-pages per page
    if mini_pages_per_page == 4:
        cols, rows = 2, 2
    elif mini_pages_per_page == 6:
        cols, rows = 2, 3
    else:
        raise ValueError("Unsupported number of mini-pages per page. Supported values are 4 and 6.")

    for group_index in range(num_groups):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=A4)

        for j in range(mini_pages_per_page):
            page_index = group_index * mini_pages_per_page + j
            if page_index < total_pages:
                page = reader.pages[page_index]
                packet_page = io.BytesIO()
                writer_single = PdfWriter()
                writer_single.add_page(page)
                writer_single.write(packet_page)

                packet_page.seek(0)
                pdf_document = fitz.open(stream=packet_page, filetype="pdf")
                pdf_page = pdf_document.load_page(0)

                # Skip blank pages
                if is_blank_page(pdf_page):
                    print(f"Skipping blank page: {page_index + 1}")
                    continue

                try:
                    pix = pdf_page.get_pixmap()
                except Exception as e:
                    print(f"Error creating pixmap for page {page_index + 1}: {e}")
                    continue

                image_packet = io.BytesIO(pix.tobytes("png"))
                image_reader = ImageReader(image_packet)

                # Calculate position for each of the mini-pages
                x_offset = (j % cols) * (page_width / cols)
                y_offset = (rows - 1 - (j // cols)) * (page_height / rows)

                # Get the original page size
                original_page_width = pdf_page.rect.width
                original_page_height = pdf_page.rect.height

                # Calculate the scaling factors
                scale_x = (page_width / cols) / original_page_width
                scale_y = (page_height / rows) / original_page_height

                # Use the smaller scaling factor to maintain aspect ratio
                scale = min(scale_x, scale_y)

                # Calculate the new width and height
                new_width = original_page_width * scale
                new_height = original_page_height * scale

                # Center the image within the allocated space
                centered_x_offset = x_offset + (page_width / cols - new_width) / 2
                centered_y_offset = y_offset + (page_height / rows - new_height) / 2

                # Draw the mini-page onto the canvas
                c.drawImage(image_reader, centered_x_offset, centered_y_offset, new_width, new_height)
                print(f"Processed page {page_index + 1}")

        c.save()
        packet.seek(0)

        # Save the temporary file
        temp_file_path = f"temp_{group_index}.pdf"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(packet.getvalue())
        temp_files.append(temp_file_path)

    # Merge all temporary files into the final output file
    merger = PdfMerger()
    for temp_file_path in temp_files:
        merger.append(temp_file_path)
    merger.write(output_pdf_path)
    merger.close()

    # Clean up temporary files
    for temp_file_path in temp_files:
        os.remove(temp_file_path)

# Example usage
root_dir = os.path.dirname(os.path.abspath(__file__))
input_dir = os.path.join(root_dir, "pdf")
output_dir = os.path.join(root_dir, "output")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Process each PDF file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith(".pdf"):
        input_pdf = os.path.join(input_dir, file_name)
        output_pdf = os.path.join(output_dir, file_name.replace(".pdf", "_comprized.pdf"))
        mini_pages_per_page = 6  # Specify the number of mini-pages per page (4 or 6)
        combine_pages(input_pdf, output_pdf, mini_pages_per_page)
        print(f"PDF successfully created: {output_pdf}")