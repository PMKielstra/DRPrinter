import csv
from tempfile import TemporaryDirectory
from os import path
import re
from zipfile import ZipFile
from pypdf import PdfWriter
from weasyprint import HTML

def para(str):
    return re.sub(r"\n+", "</p><p>", str)


def process_csv(in_file, out_file, doublesided, combine):
    with TemporaryDirectory() as tmp_path:
        csvreader = csv.reader(in_file)
        headers = csvreader.__next__()

        if combine:
            pdf = PdfWriter()
        else:
            zip = ZipFile(out_file, "w")

        bp = None

        for rownum, row in enumerate(csvreader, start=2):
            row_text = "\n\n".join(
                ["<h1>Row: {0}</h1>".format(rownum)]
                + [
                    para("<p><b>{0}</b> {1}</p>".format(headers[i], elt))
                    for i, elt in enumerate(row)
                    if elt != "" and headers[i][0] != "-"
                ]
            )
            pdf_name = "{0}.pdf".format(rownum)
            pdf_path = path.join(
                tmp_path, pdf_name
            )  # Use a named file in a temp directory to avoid potential weirdness with closing and re-opening
            HTML(string=row_text).write_pdf(pdf_path)

            if not combine:
                zip.write(pdf_path, pdf_name)
                continue

            pdf.append(pdf_path)
            if doublesided and pdf.get_num_pages() % 2 == 1:
                pdf.add_blank_page()

        if combine:
            pdf.write(out_file)
        else:
            zip.close()
