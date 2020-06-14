import sys
import traceback
from PyPDF2 import PdfFileReader, PdfFileWriter
from copy import copy

try :
    src = sys.argv[1]
except :
    src = r'/path/to/my/file.pdf'


input1 = PdfFileReader(open(src, "rb"))
output = PdfFileWriter()
nPages = input1.getNumPages()

for i in range(nPages): 
    page = input1.getPage(i)
    #print page
    if '/Annots' in page:
        for annot in page['/Annots']:
            tmp_page = copy(page)

            # Cut out each square comment
            if annot.getObject()['/Subtype'] == '/Square':
                print annot.getObject()['/Rect']
                tmp_page.cropBox.upperLeft = annot.getObject()['/Rect'][0:2]
                tmp_page.cropBox.lowerRight = annot.getObject()['/Rect'][2:4]
                output.addPage(tmp_page)
            
            # Cut out each marked text
            if annot.getObject()['/Subtype'] == '/Highlight': 
                print annot.getObject()['/Rect']
                tmp_page.cropBox.upperLeft = annot.getObject()['/Rect'][0:2]
                tmp_page.cropBox.lowerRight = annot.getObject()['/Rect'][2:4]
                output.addPage(tmp_page)

            # Cut out whole page for each vertical line 
            if annot.getObject()['/Subtype'] == '/Line':  
                print annot.getObject()['/Rect']
                tmp_page.cropBox.upperLeft = (0, annot.getObject()['/Rect'][1])
                tmp_page.cropBox.lowerRight = (page.mediaBox.getUpperRight_x(), annot.getObject()['/Rect'][3])
                output.addPage(tmp_page)


outputStream = file("test.pdf", "wb")
output.write(outputStream)
outputStream.close()

#/Rect defines the bounding box of the comment on the page/spread, in points (1/72 of an inch) relative to the lower-left corner of the page, increasing values going right and up.
# y |_ x
# For different pdf annotators: if '/QuadPoints' in annot.getObject(): # if '/L' in annot.getObject():
