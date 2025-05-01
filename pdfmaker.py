import csv
from tempfile import TemporaryDirectory
from os import path
from zipfile import ZipFile
from pdfrw import PdfReader, PdfWriter, PdfName, PdfDict
from md2pdf.core import md2pdf

def blank_page(template):
    x = PdfDict()
    x.Type = PdfName.Page
    x.Contents = PdfDict(stream="")
    x.MediaBox = template.inheritable.MediaBox
    return x

def process_csv(in_file, out_file, doublesided, combine):
    if not in_file: return        
    with TemporaryDirectory() as tmp_path:
        csvreader = csv.reader(in_file)
        headers = csvreader.__next__()

        if combine:
            pdf = PdfWriter(out_file)
        else:
            zip = ZipFile(out_file, "w")

        bp = None

        for rownum, row in enumerate(csvreader, start=2):
            row_text = '\n\n'.join(['## Row: {0}'.format(rownum)] + [
                '**{0}** {1}'.format(headers[i], elt)
                for i, elt in enumerate(row)
                if elt != '' and headers[i][0] != '-'
            ])
            pdf_name = '{0}.pdf'.format(rownum)
            pdf_path = path.join(tmp_path, pdf_name) # Use a named file in a temp directory to avoid potential weirdness with closing and re-opening
            md2pdf(pdf_file_path=pdf_path, md_content=row_text)

            if not combine:
                zip.write(pdf_path, pdf_name)
                continue

            pages = PdfReader(pdf_path).pages
            pdf.addpages(pages)
            if doublesided:
                if bp is None:
                    bp = blank_page(pages[0])

                if len(pages) % 2 != 0:
                    pdf.addpage(bp)

        if combine:
            pdf.write()
        else:
            zip.close()
