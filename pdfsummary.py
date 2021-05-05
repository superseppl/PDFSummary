import sys
import io

from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import json

def extract_information(path):
    pdf = PdfFileReader(open(path, "rb"))
    information = pdf.getDocumentInfo()

    txt = """
    Information about {path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {pdf.getNumPages()}
    """

    print(txt)
    return information

def extract_comments(path):
    inPdf = PdfFileReader(open(path, "rb"))
    outPdf = PdfFileWriter()
    nPages = inPdf.getNumPages()

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    xPos, yPos = A4

    yOffset = 50.0
    yWritingOffset = 0.0
    xWritingOffset = 0.0

    for i in range(nPages): 
        page = inPdf.getPage(i)

        if '/Annots' in page:
            for annot in page['/Annots']:
                object = annot.getObject()

                if (yOffset > yPos - 20):        
                    can.showPage()
                    yOffset = 50

                # Writings
                if object['/Subtype'] == '/PolyLine':
                    drawing = [float(o) for o in object['/Vertices']]

                    if abs(yWritingOffset - drawing[1]) > 60:
                        yOffset += 60
                        xWritingOffset = drawing[0]
                        yWritingOffset = drawing[1]
                        
                    p_x = [o - xWritingOffset + 20 for o in drawing[::2]]
                    p_y = [o + (yPos - yOffset) - yWritingOffset for o in drawing[1::2]]

                    p = can.beginPath()
                    p.moveTo(p_x[0],p_y[0])
                    for x,y in zip(p_x[1:],p_y[1:]):
                        p.lineTo(x,y)

                    can.drawPath(p)

                # Highlightet text
                if annot.getObject()['/Subtype'] == '/Highlight':
                    if "/onyxtag" in object:
                        tag = json.loads(object["/onyxtag"])
                        attr = json.loads(tag["extra_attr"])
                        can.drawString(10, yPos - yOffset, attr["quote"].encode('ascii', 'ignore'))
                        yOffset += 50

                # Cut out each square comment
                # if annot.getObject()['/Subtype'] == '/Square':
                #     print(object)
                    # print(annot.getObject()['/Rect'])
                    # tmp_page.cropBox.upperLeft = annot.getObject()['/Rect'][0:2]
                    # tmp_page.cropBox.lowerRight = annot.getObject()['/Rect'][2:4]
                    # output.addPage(tmp_page)

                # Text

                    # print(annot.getObject()['/Rect'])
                    # tmp_page.cropBox.upperLeft = annot.getObject()['/Rect'][0:2]
                    # tmp_page.cropBox.lowerRight = annot.getObject()['/Rect'][2:4]
                    # output.addPage(tmp_page)

    #             # Cut out whole page for each vertical line 
    #             if annot.getObject()['/Subtype'] == '/Line':  
    #                 print(annot.getObject()['/Rect'])
    #                 tmp_page.cropBox.upperLeft = (0, annot.getObject()['/Rect'][1])
    #                 tmp_page.cropBox.lowerRight = (page.mediaBox.getUpperRight_x(), annot.getObject()['/Rect'][3])
    #                 output.addPage(tmp_page)

    can.save()
    packet.seek(0)

    with open("test.pdf",'wb') as fp:
        fp.write(packet.getvalue())

if __name__ == '__main__':
    try :
        path = sys.argv[1]
    except :
        path = r'/path/to/my/file.pdf'

    extract_comments(path)

    

    # comment = [282.94, 642.44, 282.94, 642.44, 282.94, 642.44, 282.94, 642.44, 282.94, 642.44, 282.94, 642.24, 282.94, 641.92, 282.94, 641.51, 282.94, 640.98, 282.94, 640.25, 282.94, 639.42, 282.94, 638.38, 282.94, 637.12, 282.94, 635.66, 283.04, 634.2, 283.13, 632.74, 283.23, 631.28, 283.42, 629.93, 283.61, 628.67, 283.9, 627.53, 284.09, 626.48, 284.28, 625.65, 284.57, 624.81, 284.76, 624.19, 284.95, 623.67, 285.24, 623.25]
    
    # for i in range(0,len(comment),4):
    #     if comment[i-4:i] != []:
    #         can.line(*comment[i-4:i])

    # comment = [ int(x) for x in comment ]

    # output = PdfFileWriter()
    # new_pdf = PdfFileReader(packet)
    # output.addPage(new_pdf)
    # output.write(open("test.pdf", "wb"))

    # x, y = 0,0
	# while y + can.height < 290:
	# 	while x + can.width < 200:
	# 		can.drawOn(can, x, y)
	# 		x = x + (1 + can.width)
	# 	x = 10
	# 	y = y + (1 + barcode.height)*mm 
    
    # can.showPage() 
    # can.save()



    

#/Rect defines the bounding box of the comment on the page/spread, in points (1/72 of an inch) relative to the lower-left corner of the page, increasing values going right and up.
# y |_ x
# For different pdf annotators: if '/QuadPoints' in annot.getObject(): # if '/L' in annot.getObject():
