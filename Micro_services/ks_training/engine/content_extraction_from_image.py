import tika
from tika import parser
import numpy as np
import pandas as pd
import os
import glob
from PIL import Image
import pytesseract
import re
#from reportlab.lib.pagesizes import letter
#from reportlab.pdfgen import canvas
import io

#tika.initVM()

def perform_ocr_with_tesseract(image_path, settings):
    # Convert image to text using pytesseract
    print("Entered perform_ocr_with_tesseract")
    #image = Image.open(image_path).convert("RGB")
    image_text = pytesseract.image_to_string(image_path)
    print("image_text", image_text)

    # Create a PDF document using ReportLab
    # pdf_buffer = io.BytesIO()
    # c = canvas.Canvas(pdf_buffer, pagesize=letter)
    # c.drawString(10, 750, image_text)
    # c.save()

    # # Convert PDF buffer to bytes
    # tika_server_url = settings.TIKA_SERVER_URL
    # pdf_bytes = pdf_buffer.getvalue()

    # # Parse PDF content using Tika
    # parsed_content = parser.from_buffer(pdf_bytes, tika_server_url)

    # # Extract the text content
    # text_content = parsed_content['content']

    # Remove unwanted elements and clean up the text
    lines = image_text.split('\n')
    cleaned_lines = [
        line.replace('■■', ' ').replace('■', '').strip()
        for line in lines
        if line.strip() != '' and line.strip() != 'untitled'
    ]
    cleaned_text = '\n'.join(cleaned_lines)
    # print("cleaned_text: ", cleaned_text)
    return cleaned_text

def extract_page_id(png_filename):
    match = re.search(r'#page=(\d+)', png_filename)
    if match:
        return int(match.group(1))
    return None

def image_content_extraction_process(output_directory_hf, file_index, file_path, unwanted_pages_list, settings, group_name, doc_name_with_extension):
    try:
        page_data = []
        print("Entered image_content_extraction_process")
        if not os.path.exists(output_directory_hf):
            os.makedirs(output_directory_hf)

        last_dot_index = doc_name_with_extension.rfind(".")
        filename_without_extension = doc_name_with_extension[:last_dot_index]

        folder_c_path = os.path.join(output_directory_hf, group_name, filename_without_extension)
        #png_files = [f for f in os.listdir(folder_c_path) if f.lower().endswith(".png")]

        files_dir = []
        ext = ['png']
        [files_dir.extend(glob.glob(output_directory_hf + '/'+ group_name+ '/'+ filename_without_extension+ '/*.' + e)) for e in ext]

        for png_file in files_dir:
            print("png_file", png_file)
            page_id = extract_page_id(os.path.basename(png_file))

            if page_id is not None:
                page_content = perform_ocr_with_tesseract(png_file, settings)

                if len(unwanted_pages_list) > 0 and page_id not in unwanted_pages_list:
                    custom_file_path = file_path + "#page=" + str(page_id)
                    page_data.append({
                        "doc_id": file_index,
                        "doc_title": doc_name_with_extension,
                        "page_id": page_id,
                        "page_content": page_content,
                        "file_path": custom_file_path
                    })
                elif len(unwanted_pages_list) == 0:
                    custom_file_path = file_path + "#page=" + str(page_id)
                    page_data.append({
                        "doc_id": file_index,
                        "doc_title": doc_name_with_extension,
                        "page_id": page_id,
                        "page_content": page_content,
                        "file_path": custom_file_path
                    })

        return page_data

    except Exception as e:
        print("Text extraction from image process failed:", str(e))