from abc import ABC, abstractmethod
from io import BytesIO
from zipfile import ZipFile

from pypdf import PdfWriter

class OutputHandler(ABC):
    @abstractmethod
    def __init__(self, out_file):
        pass

    @abstractmethod
    def append_bytes(self, rownum, bytes):
        pass

    @abstractmethod
    def close(self):
        pass

class PdfOutputHandler(OutputHandler):
    def __init__(self, out_file):
        self.out_file = out_file
        self.pdf = PdfWriter()

    def append_bytes(self, rownum, bytes):
        self.pdf.append(BytesIO(bytes))

    def close(self):
        self.pdf.write(self.out_file)

class DoublesidedPdfOutputHandler(PdfOutputHandler):
    def append_bytes(self, rownum, bytes):
        super().append_bytes(rownum, bytes)
        if self.pdf.get_num_pages() % 2 == 1:
            self.pdf.add_blank_page()

class ZipOutputHandler(OutputHandler):
    def __init__(self, out_file):
        self.zip = ZipFile(out_file, "w")

    def append_bytes(self, rownum, bytes):
        self.zip.writestr(f"{rownum}.pdf", bytes)

    def close(self):
        self.zip.close()