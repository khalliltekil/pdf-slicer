import io
import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

def combine_pages(input_pdf_path, output_pdf_path, mini_pages_per_page):
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    page_width, page_height = letter

    # Determine the layout based on the number of mini-pages per page
    if mini_pages_per_page == 4:
        cols, rows = 2, 2
    elif mini_pages_per_page == 6:
        cols, rows = 2, 3
    else:
        raise ValueError("Unsupported number of mini-pages per page. Supported values are 4 and 6.")

    for i in range(0, len(reader.pages), mini_pages_per_page):
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)

        for j in range(mini_pages_per_page):
            if i + j < len(reader.pages):
                page = reader.pages[i + j]
                packet_page = io.BytesIO()
                writer_single = PdfWriter()
                writer_single.add_page(page)
                writer_single.write(packet_page)

                packet_page.seek(0)
                pdf_document = fitz.open(stream=packet_page, filetype="pdf")
                pdf_page = pdf_document.load_page(0)
                pix = pdf_page.get_pixmap()
                image_packet = io.BytesIO(pix.tobytes("png"))
                image_reader = ImageReader(image_packet)

                # Calculate position for each of the mini-pages
                x_offset = (j % cols) * (page_width / cols)
                y_offset = (rows - 1 - (j // cols)) * (page_height / rows)

                # Draw the mini-page onto the canvas
                c.drawImage(image_reader, x_offset, y_offset, page_width / cols, page_height / rows)

        c.save()
        packet.seek(0)

        # Add the newly created page to the writer
        new_page = PdfReader(packet).pages[0]
        writer.add_page(new_page)

    # Write the output file
    with open(output_pdf_path, "wb") as output_file:
        writer.write(output_file)

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