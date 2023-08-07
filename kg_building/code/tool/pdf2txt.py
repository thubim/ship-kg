import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

def parserpdf(file_name, save_name):
    fp = open(file_name, 'rb')
    output = open(save_name,'w+')
    # Create a PDF parser object associated with the file object
    parser = PDFParser(fp)
    # Create a PDF document object that stores the document structure.
    # Password for initialization as 2nd parameter
    document = PDFDocument(parser)
    # Check if the document allows text extraction. If not, abort.
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    # Create a PDF resource manager object that stores shared resources.
    rsrcmgr = PDFResourceManager()
    # Create a PDF device object.
    #device = PDFDevice(rsrcmgr)
    # BEGIN LAYOUT ANALYSIS.
    # Set parameters for analysis.
    laparams = LAParams(
        char_margin=10.0,
        line_margin=0.2,
        boxes_flow=0.2,
        all_texts=False,
    )
    # Create a PDF page aggregator object.
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # Create a PDF interpreter object.
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    # loop over all pages in the document
    for page in PDFPage.create_pages(document):
        # read the page into a layout object
        interpreter.process_page(page)
        layout = device.get_result()
        for obj in layout._objs:
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                results = obj.get_text()
                output.write(results)
    print("完成")

if __name__ == '__main__':
    input_path = '../../规范/《钢质海船入级规范》2018.pdf'
    output_path = '../../data/input_text.txt'
    print("开始")
    parserpdf(input_path, output_path)













