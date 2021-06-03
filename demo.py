from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
import random 
import string
import time
from canvasapi import Canvas as Lms
API_URL = "https://canvas.oregonstate.edu/"
# Canvas API key
API_KEY = "1002~m1ShsxLu5bZY6SbSd5KlXjN9ejluixXwRFVYDvVQhGjIMx46dLJqS81NfZtCeTRJ"


def create_watermark(input_pdf, output, watermark, x=random.randint(0,300),y=random.randint(0,500)):
    c = canvas.Canvas(watermark)
    c.globalAlpha = 0.1;
    # Draw the image at x, y. I positioned the x,y to be where i like here
    c.drawImage('src_2.png', x, y,width=300,height=300,mask='auto')

    # Add some custom text for good measure
    lms = Lms(API_URL, API_KEY)

    course = lms.get_course(1836569)
    c.drawString(30, 30,"Oregonstate: "+str(course))
    c.drawString(30, 750,str(int(time.time()) ))
    temp = "Spongebob".encode('utf-8')
    r = ["0x{:04x}".format(c)[2:] for c in temp ]
    code = "".join(r)
    code = code.upper()
    print(code)
    print(code[::-1])
    c.drawString(320, 750,code[::-1])
    c.save()
    
    watermark_obj = PdfFileReader(watermark)
    watermark_page = watermark_obj.getPage(0)
 
    pdf_reader = PdfFileReader(input_pdf)
    pdf_writer = PdfFileWriter()
    pdf_merger = PdfFileMerger()
    for page in range(pdf_reader.getNumPages()):
        page = pdf_reader.getPage(page)
        page.mergePage(watermark_page)
        pdf_writer.addPage(page)
 
    with open(output, 'wb') as out:
        pdf_writer.write(out)
 
if __name__ == '__main__':
    a = 'input.pdf'
    b = 'watermark.pdf'
    c = 'watermark_small.pdf'
    create_watermark(\
        input_pdf=a,\
        output='watermarked.pdf',\
        watermark=b,\
        x = 150,\
        y = 250 \
    )