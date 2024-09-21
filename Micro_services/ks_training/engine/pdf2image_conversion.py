import os
import json
from pdf2image import convert_from_path


def pdf_to_image_conversion(input_directory, op_dir_and_ip_dir_image, group_name, doc_name_with_extension):
    try:
        def convert_pdf_to_png(pdf_path, output_folder, file_name_format):
            images = convert_from_path(pdf_path, 500, poppler_path = r"C:\Python\poppler-24.02.0\Library\bin")
            for i, image in enumerate(images):
                image_name = f"{file_name_format}#page={i + 1}.png"
                image_path = os.path.join(output_folder, image_name)
                image.save(image_path, "PNG")

        group_folder = os.path.join(op_dir_and_ip_dir_image, group_name)

        # Find the position of the last dot (.) in the filename
        last_dot_index = doc_name_with_extension.rfind(".")

        # Extract the filename without the extension
        filename_without_extension = doc_name_with_extension[:last_dot_index]
        print("Filename without extension:", filename_without_extension)

        doc_folder = os.path.join(group_folder, filename_without_extension)

        if not os.path.exists(doc_folder):
            os.makedirs(doc_folder)

        if group_name in os.listdir(input_directory):
            input_folder = os.path.join(input_directory, group_name)
            pdf_file_path = os.path.join(input_folder, doc_name_with_extension)

            if os.path.exists(pdf_file_path):
                output_folder = doc_folder
                convert_pdf_to_png(pdf_file_path, output_folder, filename_without_extension)  # Pass the file name format
                print(f"Converted and saved images for {doc_name_with_extension}")

        return "PDF to IMAGE Conversion process completed."
    except Exception as e:
        print("PDF to IMAGE Conversion process failed", str(e))
          
def pdftoimage(input_file_path, out_path, page_number):       
    pdf_image_pages = convert_from_path(input_file_path, 500, first_page=page_number, last_page=page_number)
    image_counter = 0  
    paths = []
    
    for page in pdf_image_pages:
        filename = out_path + "output_page.png"
        page.save(filename, 'PNG')
        paths.append(filename)
    return paths
