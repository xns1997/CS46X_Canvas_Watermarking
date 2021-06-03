from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from reportlab.pdfgen import canvas
import random 
import string
import time
import os
import configparser

class water:
    def __init__(self,inputFile="",watermarkDir="",config = "",info={}):
        self.canvas = canvas.Canvas('temp.pdf')
        self.srcDir = inputFile
        self.wmDir  = watermarkDir
        self.width = 300
        self.height = 500
        self.info = info
        self.out = ""
        try:
            self.config = configparser.ConfigParser()
            self.config.read(config)
            self.readDefaultConfig()
        except:
            print('Error: init')

    def readDefaultConfig(self):
        errPlace = ""
        try:
            c = self.config['Default']
            errPlace = 'alpha'
            self.canvas.globalAlpha = c['alpha']
            errPlace = 'font'
            self.canvas.setFont(c['Font'],int(c['FontSize']))
            errPlace = 'fontRGB'
            self.canvas.setFillColorRGB(float(c['FontColorR']),float(c['FontColorG']),float(c['FontColorB']))
            errPlace = 'Page'
            self.width = int(c['PageWidth'])
            self.height = int(c['PageHeight'])
        except:
            print('Error: readDefaultConfig - ', errPlace)
            
    def imgWM(self,\
        x = -1,y = -1,\
        w = 300, h = 300):
        if x == -1:
            x = random.randint(0,self.width)
        if y == -1:
            y = random.randint(0,self.width) 
        self.canvas.drawImage(self.wmDir, x, y, width = w, height = h, mask = 'auto')

    def strWM(self,\
        x = 0, y = 0,\
        src = "",):
        self.canvas.drawString(x,y,src)

    def merge(self):
        self.canvas.save()
        watermark_obj = PdfFileReader('temp.pdf')
        watermark_page = watermark_obj.getPage(0)
 
        pdf_reader = PdfFileReader(self.srcDir)
        pdf_writer = PdfFileWriter()
        pdf_merger = PdfFileMerger()
        for page in range(pdf_reader.getNumPages()):
            page = pdf_reader.getPage(page)
            page.mergePage(watermark_page)
            pdf_writer.addPage(page)
        filepath,fullflname = os.path.split(self.srcDir)
        fname,ext = os.path.splitext(fullflname)
        if filepath == ".":
            filepath = "./"
        output = filepath + "/"+ fname + "_out" + ext
        self.out = fname + "_out" + ext
        with open(output, 'wb') as out:
            pdf_writer.write(out)
    def do(self):
        self.imgWM()
        n = "oregonstate" + str(random.randint(0,1000000))
        import hashlib
        md5 = hashlib.md5()
        s = self.info['name'] + str(int(time.time()) )
        md5.update(s.encode('utf-8'))
        self.strWM(30, 30, md5.hexdigest())
        self.strWM(250, 750, self.info['title']+"_"+self.info['id'])
        self.strWM(250, 30, self.info['inst'])
        self.strWM(30, 750, str(int(time.time()) ))
        self.merge()
        return self.out
