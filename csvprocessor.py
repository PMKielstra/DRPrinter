import csv
import re
from weasyprint import HTML

from outputhandler import PdfOutputHandler, DoublesidedPdfOutputHandler, ZipOutputHandler

def para(str):
    return re.sub(r"\n+", "</p><p>", str)

def process_csv(in_file, out_file, doublesided, combine):
    csvreader = csv.reader(in_file)
    headers = csvreader.__next__()

    if combine:
        if doublesided:
            handler = DoublesidedPdfOutputHandler(out_file)
        else:
            handler = PdfOutputHandler(out_file)
    else:
        handler = ZipOutputHandler(out_file)

    for rownum, row in enumerate(csvreader, start=2):
        row_text = "\n\n".join(
            ["<h1>Row: {0}</h1>".format(rownum)]
            + [
                para("<p><b>{0}</b> {1}</p>".format(headers[i], elt))
                for i, elt in enumerate(row)
                if elt != "" and headers[i][0] != "-"
            ]
        )

        this_row_bytes = HTML(string=row_text).write_pdf()
        handler.append_bytes(rownum, this_row_bytes)

    handler.close()
