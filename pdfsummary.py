import sys, os
import io
import json

from PyPDF2 import PdfFileReader, PdfFileWriter

from reportlab.platypus.flowables import Flowable
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

class HandAnnotation(Flowable, object):
    def __init__(self, start):
        super(Flowable, self).__init__()
        self.width=A4[1]
        self.height=70

        self.start = start
        self.vertices = []
        #self._showBoundary = 1

    def __repr__(self):
        return ("Annotation start: {}".format(self.start))

    def __add__(self, vertices):
        self.vertices.append(vertices)

    def update_height(self):
        yMax = max(max([o[1::2] for o in self.vertices]))
        yMin = min(min([o[1::2] for o in self.vertices]))
        self.height = (yMax - yMin) + 10
        self.start[1] = yMin

    def draw(self):
        for v in self.vertices:
            p_x = [o - self.start[0] for o in v[::2]]
            p_y = [o - self.start[1] for o in v[1::2]]

            p = self.canv.beginPath()
            p.moveTo(p_x[0],p_y[0])
            for x,y in zip(p_x[1:],p_y[1:]):
                p.lineTo(x,y)
            self.canv.drawPath(p)

class PDFCut(Flowable, object):
    def __init__(self, img):
        super(Flowable, self).__init__()
        self.width, self.height = img.size
        self.img = img
        #self._showBoundary = 1

    def __repr__(self):
        return ("Annotation start: {}".format(self.start))

    def draw(self):
        self.canv.drawInlineImage(self.img, 0,0)

class PDFSummary():
    def __init__(self):
        pass

    def check_folder(self, path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path,f))]
        files = filter(lambda f: f.endswith(('.pdf','.PDF')), files)

        story = []
        for f in files:
            print("Check file {}".format(f))
            self.extract_informationc(f, path)
            story += self.check_file(f, path)

        outPdf = SimpleDocTemplate("summary.pdf",pagesize = A4)
        outPdf.build(story)

    def extract_informationc(self,file, path=""):
        inPdf = PdfFileReader(open(os.path.join(path,file), "rb"))
        information = inPdf.getDocumentInfo()

        txt = f"""
        Information about {file}:

        Author: {information.author}
        Creator: {information.creator}
        Producer: {information.producer}
        Subject: {information.subject}
        Title: {information.title}
        Number of pages: {inPdf.getNumPages()}
        """

        print(txt)
        return information

    def check_file(self,file, path=""):
        inPdf = PdfFileReader(open(os.path.join(path,file), "rb"))
        nPages = inPdf.getNumPages()

        styles = getSampleStyleSheet()
        story = []

        handAnnotation = None

        for i in range(nPages):
            page = inPdf.getPage(i)

            if '/Annots' in page:
                for annot in page['/Annots']:
                    object = annot.getObject()

                    # Highlightet text
                    if annot.getObject()['/Subtype'] == '/Highlight':
                        if object['/Contents'] != '':
                            story.append(Paragraph(object['/Contents'].encode('ascii', 'ignore'), styles['Normal']))

                        if "/onyxtag" in object:
                            tag = json.loads(object["/onyxtag"])
                            attr = json.loads(tag["extra_attr"])
                            story.append(Paragraph(attr["quote"].encode('ascii', 'ignore'), styles['Normal']))

                    # Writings
                    if object['/Subtype'] == '/PolyLine':
                        vertices = [float(o) for o in object['/Vertices']]

                        if handAnnotation is None:
                            handAnnotation = HandAnnotation(vertices[:2])
                            handAnnotation + vertices
                        elif abs(handAnnotation.start[1] - vertices[1]) > 50:
                            handAnnotation.update_height()
                            story.append(handAnnotation)

                            handAnnotation = HandAnnotation(vertices[:2])
                            handAnnotation + vertices
                        else:
                            handAnnotation + vertices

                    # Cut out each square comment
                    if object['/Subtype'] == '/Polygon':
                        pdfWriter = PdfFileWriter()
                        pdfWriter.addPage(page)

                        pdfBytes = io.BytesIO()
                        pdfWriter.write(pdfBytes)
                        pdfBytes.seek(0)

                        tag = json.loads(object["/onyxtag"])
                        attr = json.loads(tag["extra_attr"])
                        p1 = attr["points"][0]
                        p2 = attr["points"][1]

                        from pdf2image import convert_from_bytes
                        size=(page.mediaBox.getWidth(), page.mediaBox.getHeight())
                        img = convert_from_bytes(pdfBytes.getvalue(), size=size)[0]
                        img = img.crop((p1["x"]+1,p1["y"]+1,p2["x"]-1,p2["y"]-1))

                        if (img.size > (0.0,0.0)):
                            story.append(PDFCut(img))

        return story

if __name__ == '__main__':
    try :
        path = sys.argv[1]
    except :
        path = r'/path/to/my/file.pdf'

    pdfSummary = PDFSummary()
    pdfSummary.check_folder(path)
