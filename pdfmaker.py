import csv
from tempfile import TemporaryDirectory
from os import path, makedirs
from pypdf import PdfWriter
from md2pdf.core import md2pdf

def process_csv(in_file, out_file):
    with TemporaryDirectory() as tmp_path:
        if not in_file: return        
        csvreader = csv.reader(in_file)
        headers = csvreader.__next__()

        pdf = PdfWriter()

        for rownum, row in enumerate(csvreader, start=2):
            row_text = '\n\n'.join([f'## Row: {rownum}'] + [
                f'**{headers[i]}** {elt}'
                for i, elt in enumerate(row)
                if elt != '' and headers[i][0] != '-'
            ])
            pdf_path = path.join(tmp_path, f'{rownum}.pdf') # Use a named file in a temp directory to avoid potential weirdness with closing and re-opening
            md2pdf(pdf_file_path=pdf_path, md_content=row_text)
            
            pdf.append(pdf_path)
            if len(pdf.pages) % 2 != 0:
                pdf.add_blank_page()

        pdf.write(out_file)
