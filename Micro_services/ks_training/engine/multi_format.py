import os, datetime
from PyPDF2 import PdfReader
import engine.utils as utility


import subprocess
# path_to_office = r"C:\Python\LibreOffice\program\soffice.exe"   # path to the engine

def multi_format_process(api_data, settings, channel, connection):
    project_code = api_data["project_code"]
    group_name = api_data["group_name"]
    files_name = api_data["files_name"]
    api_data['zid'] = ' '
    input_directory, _, _, _, _, _, _ = utility.select_folder_dir(api_data, settings)

    for file_name in files_name:
        try:
            responseDict = {}
            file_path = input_directory+group_name+'/'+file_name
            ws_path = input_directory+group_name+'/'
            print("file_path", file_path)

            split_filename = os.path.split(file_path)
            filename = split_filename[-1]
            print("filename", filename)
            filename_without_extension = os.path.splitext(filename)[0]
            # print("filename_without_extension", filename_without_extension)
            file_extension = os.path.splitext(filename)[-1].lower()
            # print("file_extension", file_extension)
            output_folder = input_directory+group_name+'/'

            if file_extension in [".doc", ".docx", ".ppt", ".pptx"]:
                if os.path.exists(file_path):
                    print("File exists")
                else:
                    print("File does not exist")
                # subprocess.call([path_to_office, "--headless", "--convert-to", "pdf", file_path , "--outdir", output_folder])
                # subprocess.call(["libreoffice", "--headless", "--convert-to", "pdf", file_path , "--outdir", output_folder])
                command = f"docker run --rm -v {ws_path}:/workspace -e INPUT_FILE=/workspace/{filename}  -e OUPUT_DIR=/workspace/ localhost/libreoffice-custom"
                # command = ["libreoffice --headless --convert-to pdf", file_path , "--outdir", output_folder]
                subprocess.call(command)
                print("successssdddd")
                responseDict = utility.form_success_response(responseDict, ' ', ' ', ' ', api_data)
            else:
                err_msg = "ERROR!!! Please upload supported formats (doc|docx|ppt|pptx|pdf)"
                print("err_msg", err_msg)
                responseDict = utility.form_error_response(responseDict, err_msg, api_data, file_name)
            
            pdf_path = input_directory+group_name+'/'+filename_without_extension+".pdf"
            pdf_file_page = PdfReader(pdf_path)
            total_pages = len(pdf_file_page.pages)
            print("total_pages", total_pages)
            
            responseDict["total_pages"] = total_pages
            responseDict["file_name"] = file_name
            responseDict["category"] = "pdf_convert"
            utility.publish_results(channel, responseDict, project_code, settings, connection)
        except Exception as e:
            responseDict = {}
            job_date = datetime.datetime.now()
            responseDict["job_date"] = str(job_date)
            responseDict = utility.form_error_response(responseDict, str(e), api_data, file_name)
            responseDict["category"] = "pdf_convert"
            utility.publish_results(channel, responseDict, project_code, settings, connection)