import io
import os
import fitz  # PyMuPDF
import logging
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PDFCombiner:
    def __init__(self, mini_pages_per_page):
        if mini_pages_per_page not in [4, 6]:
            raise ValueError("Unsupported number of mini-pages per page. Supported values are 4 and 6.")
        self.mini_pages_per_page = mini_pages_per_page
        self.page_width, self.page_height = A4
        self.cols, self.rows = (2, 2) if mini_pages_per_page == 4 else (2, 3)

    def is_blank_page(self, pdf_page):
        """Check if a PDF page is blank by examining its text content."""
        text = pdf_page.get_text()
        return not text.strip()

    def combine_pages(self, input_pdf_path, output_pdf_path):
        reader = PdfReader(input_pdf_path)
        total_pages = len(reader.pages)
        num_groups = (total_pages + self.mini_pages_per_page - 1) // self.mini_pages_per_page  # Ceiling division

        temp_files = []

        for group_index in range(num_groups):
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)

            for j in range(self.mini_pages_per_page):
                page_index = group_index * self.mini_pages_per_page + j
                if page_index < total_pages:
                    page = reader.pages[page_index]
                    packet_page = io.BytesIO()
                    writer_single = PdfWriter()
                    writer_single.add_page(page)
                    writer_single.write(packet_page)

                    packet_page.seek(0)
                    try:
                        pdf_document = fitz.open(stream=packet_page, filetype="pdf")
                    except Exception as e:
                        logging.error(f"Error opening PDF document for page {page_index + 1}: {e}")
                        continue

                    pdf_page = pdf_document.load_page(0)

                    # Skip blank pages
                    if self.is_blank_page(pdf_page):
                        logging.debug(f"Skipping blank page: {page_index + 1}")
                        continue

                    try:
                        pix = pdf_page.get_pixmap()
                    except Exception as e:
                        logging.error(f"Error creating pixmap for page {page_index + 1}: {e}")
                        continue

                    image_packet = io.BytesIO(pix.tobytes("png"))
                    image_reader = ImageReader(image_packet)

                    # Calculate position for each of the mini-pages
                    x_offset = (j % self.cols) * (self.page_width / self.cols)
                    y_offset = (self.rows - 1 - (j // self.cols)) * (self.page_height / self.rows)

                    # Get the original page size
                    original_page_width = pdf_page.rect.width
                    original_page_height = pdf_page.rect.height

                    # Calculate the scaling factors
                    scale_x = (self.page_width / self.cols) / original_page_width
                    scale_y = (self.page_height / self.rows) / original_page_height

                    # Use the smaller scaling factor to maintain aspect ratio
                    scale = min(scale_x, scale_y)

                    # Calculate the new width and height
                    new_width = original_page_width * scale
                    new_height = original_page_height * scale

                    # Center the image within the allocated space
                    centered_x_offset = x_offset + (self.page_width / self.cols - new_width) / 2
                    centered_y_offset = y_offset + (self.page_height / self.rows - new_height) / 2

                    # Draw the mini-page onto the canvas
                    c.drawImage(image_reader, centered_x_offset, centered_y_offset, new_width, new_height)
                    logging.debug(f"Processed page {page_index + 1}")

            c.save()
            packet.seek(0)

            # Save the temporary file
            temp_file_path = f"temp_{group_index}.pdf"
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(packet.getvalue())
            temp_files.append(temp_file_path)

        self.merge_temp_files(temp_files, output_pdf_path)

    def merge_temp_files(self, temp_files, output_pdf_path):
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
if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(root_dir, "pdf")
    output_dir = os.path.join(root_dir, "output")

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Process each PDF file in the input directory
    combiner = PDFCombiner(mini_pages_per_page=6)
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".pdf"):
            input_pdf = os.path.join(input_dir, file_name)
            output_pdf = os.path.join(output_dir, file_name.replace(".pdf", "_comprized.pdf"))
            combiner.combine_pages(input_pdf, output_pdf)
            logging.info(f"PDF successfully created: {output_pdf}")