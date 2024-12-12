# PDF Page Combiner

This Python script combines multiple pages of a PDF into a single page. It supports combining 4 or 6 pages into one and handles different page sizes. The output PDF pages are in Outputs in A4 size or letter size.

## Features

- Combine multiple pages into a single page
- Supports 4 or 6 mini-pages per page
- Handles different page sizes
- Skips blank pages
- Outputs in A4 size or letter size
- Processes all PDF files in a specified input directory
- Saves the output PDFs in a specified output directory with `_comprized` appended to the file names

## Requirements

- Python 3.x
- PyMuPDF
- PyPDF2
- ReportLab

## Installation

1. Clone the repository or download the script.
2. Install the required Python packages:

```sh
pip install pymupdf pypdf2 reportlab