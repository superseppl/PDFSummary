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

first = True;

for i in range(nPages): 
    page = input1.getPage(i)
    #print page
    if '/Annots' in page:
        for annot in page['/Annots']:
            tmp_page = copy(page)
            #print annot.getData()
            if '/QuadPoints' in annot.getObject():
                print annot.getObject()['/QuadPoints']
                tmp_page.cropBox.upperLeft = annot.getObject()['/QuadPoints'][0:2]
                tmp_page.cropBox.upperRight = annot.getObject()['/QuadPoints'][2:4]
                tmp_page.cropBox.lowerLeft = annot.getObject()['/QuadPoints'][4:6]
                tmp_page.cropBox.lowerRight = annot.getObject()['/QuadPoints'][6:8]
                output.addPage(tmp_page)

outputStream = file("test", "wb")
output.write(outputStream)
outputStream.close()

#/Rect defines the bounding box of the comment on the page/spread, in points (1/72 of an inch) relative to the lower-left corner of the page, increasing values going right and up.
# y |_ x
