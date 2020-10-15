from io import StringIO
import PyPDF2
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from image_utils import *
from important_functions import *


# Overal text extraction from a file
def extract_text_in_file(file_path, pdf_splitter_path, doc_language):
    if file_path.lower().endswith('pdf'):
        return text_from_split_pdf_file(pdf_splitter_path, file_path, doc_language)
    elif file_path.endswith('JPG'):
        return text_from_image_file(file_path, doc_language)
    else:
        return text_from_image_file_original(file_path, doc_language)


# Extract text from an image file
def text_from_image_file_original(file_path, doc_lang):
    img = cv2.imread(file_path)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
    lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)
    angles = []
    for x1, y1, x2, y2 in lines[0]:
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
        angles.append(angle)
    median_angle = np.median(angles)
    img_rotated = ndimage.rotate(img, median_angle)
    return pytesseract.image_to_string(img_rotated, config=doc_lang)


# Extract text from an image file
def text_from_image_file(file_path, doc_lang):
    img = cv2.imread(file_path)
    deskew = skew_correction(img)
    background_mask_removal = remove_water_mask(deskew)
    adaptive_thresh = cv2.adaptiveThreshold(background_mask_removal, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 31, 2)
    custom_config = r'--oem 3 -l eng+deu --psm 6'
    return pytesseract.image_to_string(adaptive_thresh, config=doc_lang)


# Extract text from a licence size image file
def text_from_licence_image_file(file_path, doc_lang):
    img = cv2.imread(file_path)
    img = resize_image_size(img)
    deskew = skew_correction(img)
    grayed = get_grayscale(deskew)
    return pytesseract.image_to_string(grayed, config=doc_lang + ' --psm 11')


# Extract text from a receipt size image file
def text_from_licence_plain_receipt_file(file_path, doc_lang):
    img = cv2.imread(file_path)
    img = resize_image_size(img)
    deskew = skew_correction(img)
    grayed = get_grayscale(deskew)
    return pytesseract.image_to_string(grayed, config=doc_lang)


# Extract text from a pdf file
def convert_pdf_to_txt(file_path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, laparams=laparams)
    fp = open(file_path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text


# split a pdf into smaller pieces 1 page each before processing them
def text_from_split_pdf_file(pdf_processing_folder, file_path, doc_lang):
    return_text = ''
    pdf = PyPDF2.PdfFileReader(file_path, strict=False)
    for page in range(pdf.getNumPages()):
        pdf_writer = PyPDF2.PdfFileWriter()
        pdf_writer.addPage(pdf.getPage(page))
        output = f'{pdf_processing_folder}/Split-{page}.pdf'
        with open(output, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        print(f'Processing Page {str(page)}/{str(pdf.getNumPages())} of file ==>{file_path}')
        page_text = convert_pdf_to_txt(f'{pdf_processing_folder}/Split-{page}.pdf')
        return_text = return_text + page_text + '\n'
        if not re.search('[a-zA-Z]+', page_text):
            create_folder(pdf_processing_folder, 'PDF_IMAGES')
            return_text = return_text + text_from_pdf_image_split_file(f'{pdf_processing_folder}/PDF_IMAGES',
                                                                       f'{pdf_processing_folder}/Split-{page}.pdf',
                                                                       doc_lang) + '\n'
    return return_text


# split a pdf into smaller pieces 1 page each before processing them
def text_from_pdf_image_split_file(pdf_processing_folder, file_path, doc_lang):
    convert_pdf_to_image_and_save(file_path, pdf_processing_folder)
    img = cv2.imread(f'{pdf_processing_folder}/output.jpg')
    return_text = pytesseract.image_to_string(img, config=doc_lang)
    # return_text = text_from_image_file_original(img, doc_lang)
    delete_file(f'{pdf_processing_folder}/output.jpg')
    os.rmdir(f'{pdf_processing_folder}')
    return return_text
