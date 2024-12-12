# FILE: pdf_reader_ui.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox, QMessageBox
from PyQt5.QtCore import Qt
from pdf_combiner import PDFCombiner

class PDFReaderUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Reader and Combiner")
        self.setGeometry(100, 100, 800, 600)

        self.pdf_combiner = None
        self.initUI()

    def initUI(self):
        self.label = QLabel("Select a PDF file to combine pages", self)
        self.label.setAlignment(Qt.AlignCenter)

        self.open_button = QPushButton("Open PDF", self)
        self.open_button.clicked.connect(self.open_pdf)

        self.combine_button = QPushButton("Combine Pages", self)
        self.combine_button.clicked.connect(self.combine_pages)
        self.combine_button.setEnabled(False)

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(["4", "6"])
        self.combo_box.setCurrentIndex(1)  # Default to 6 mini-pages per page

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.open_button)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.combine_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_pdf(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)", options=options)
        if file_name:
            self.pdf_combiner = PDFCombiner(mini_pages_per_page=int(self.combo_box.currentText()))
            self.input_pdf_path = file_name
            self.label.setText(f"Selected PDF: {file_name}")
            self.combine_button.setEnabled(True)

    def combine_pages(self):
        if self.pdf_combiner and hasattr(self, 'input_pdf_path'):
            output_pdf_path, _ = QFileDialog.getSaveFileName(self, "Save Combined PDF", "", "PDF Files (*.pdf)")
            if output_pdf_path:
                try:
                    self.pdf_combiner.combine_pages(self.input_pdf_path, output_pdf_path)
                    QMessageBox.information(self, "Success", f"PDF successfully created: {output_pdf_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader_ui = PDFReaderUI()
    reader_ui.show()
    sys.exit(app.exec_())