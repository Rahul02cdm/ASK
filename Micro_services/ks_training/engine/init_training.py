import os, glob, sys, json, datetime, logging
from datetime import date
import pika
import pika.exceptions
import engine.utils as utility
import numpy as np
import pandas as pd

import re
import engine.create_index as index_creation
import engine.pdf2image_conversion as pdf_to_image
import engine.image_header_footer_removal as header_footer
import engine.content_extraction_from_image as image_to_text
import engine.pdf2csv as extract_service
import engine.vector_embeddings as vector_embeddings_creation
import logging
from datetime import date

# os.environ["http_proxy"] = os.environ.get('http_proxy')
# os.environ["https_proxy"] = os.environ.get('https_proxy')
# os.environ["HTTP_PROXY"] = os.environ.get('HTTP_PROXY')
# os.environ["HTTPS_PROXY"] = os.environ.get('HTTPS_PROXY')

def extract_documets_data(channel, api_data, settings, connection, es_client, embeddings):
    try:
        input_directory, output_directory, op_dir_and_ip_dir_image, output_directory_hf, models_directory, log_dir, _ = utility.select_folder_dir(api_data, settings)
        print("input_directory", input_directory)
        # utility.output_dir_handling(output_directory)
        responseDict = {}
        group_index_list = []
        
        # utility.logger_dir_handling(log_dir)
        # today = date.today()
        # d1 = today.strftime("%d-%m-%Y")
        # logger_file = log_dir+"/"+"ie_"+d1+".log"
        # logging.basicConfig(filename=logger_file, level=logging.INFO, format='%(asctime)s %(message)s')
        # logging.info('\n')
        # logging.info('Process Started')
        print('Process Started')
        
        number_of_folders = len(next(os.walk(input_directory))[1])
        print("Number of folders", number_of_folders)
        # logging.info('Number of folders %s', number_of_folders)

        directory_names = os.listdir(input_directory)
        print("Actual group_names", directory_names)

        train_files = api_data["train_files"]
        group_names = []
        for i in train_files:
            group_name = i['group_name']
            group_names.append(group_name)
        print("Needed group_names", group_names)

        for directory_name in directory_names:
            print("directory_name", directory_name)
            # logging.info('directory_name %s', directory_name)
            if directory_name in group_names:
                directory_index = group_names.index(directory_name)
                print('directory position is: ', directory_index)

                final_df = pd.DataFrame(columns=["doc_id", "doc_title", "page_id", "page_content", "file_path"])

                files_dir = []
                ext = ['pdf']
                [files_dir.extend(glob.glob(input_directory + '/'+ directory_name+ '/*.' + e)) for e in ext]
                print("Actual files_dir", files_dir)
                for file_index, input_file in enumerate(files_dir):
                    print("input_file", input_file)
                    # logging.info('input_file %s', input_file)
                    split_filename = os.path.split(input_file)
                    filename_pdf = split_filename[-1]
                    print("filename_pdf", filename_pdf)
                    # logging.info('filename_pdf %s', filename_pdf)

                    if api_data['process_type'] == "all":
                        print("process_type - all")
                        pass
                    else:
                        file_names = []
                        doc_ids = []
                        group_id = train_files[directory_index]["group_id"]
                        ks_documents = train_files[directory_index]['ks_documents']
                        for i in ks_documents:
                            doc_name = i['doc_name']
                            doc_name_without_ext = os.path.splitext(doc_name)[0]
                            doc_ext = os.path.splitext(doc_name)[-1].lower()
                            if doc_ext != ".pdf":
                                file_name = doc_name_without_ext + '.pdf'
                            else:
                                file_name = doc_name
                            
                            doc_id = i['doc_id']
                            doc_ids.append(doc_id)
                            file_names.append(file_name)
                        print(" Needed file_names", file_names)
                        if filename_pdf in file_names:
                            document_index = file_names.index(filename_pdf)
                            print('document position is: ', document_index)
                            pass
                        else:
                            continue
                    print("Go to process")

                    doc_name_with_extension = filename_pdf
                    unwanted_pages_list = ks_documents[document_index]['unwanted_pages']
                    header_offset_value = ks_documents[document_index]['header_offset']
                    footer_offset_value = ks_documents[document_index]['footer_offset']
                    print("unwanted_pages_list: ", unwanted_pages_list)
                    print("header_offset_value: ", header_offset_value)
                    print("footer_offset_value: ", footer_offset_value)

                    if header_offset_value == 0 and footer_offset_value == 0:
                        doc_pages = extract_service.tika_ocr_individual_files(file_index, input_file, filename_pdf, unwanted_pages_list, settings)
                    else:
                        image_details = pdf_to_image.pdf_to_image_conversion(input_directory, op_dir_and_ip_dir_image, group_name, doc_name_with_extension)
                        print("image_details", image_details)
                        image_hf_removal = header_footer.image_header_footer_removal_process(op_dir_and_ip_dir_image, output_directory_hf, group_name, doc_name_with_extension, header_offset_value, footer_offset_value)
                        print("image_hf_removal", image_hf_removal)
                        print("extraction start")
                        logging.info('extraction start')
                        doc_pages = image_to_text.image_content_extraction_process(output_directory_hf, file_index, input_file, unwanted_pages_list, settings, group_name, doc_name_with_extension)
                        print("extraction end")
                        logging.info('extraction end')

                    df1 = pd.DataFrame.from_records(doc_pages)
                    final_df = pd.concat([final_df, df1], axis=0, ignore_index=True)
                    final_df.drop_duplicates(keep="first", inplace=True)

                final_df['doc_id'] = final_df['doc_id'].astype('str')
                final_df['page_id'] = final_df['page_id'].astype('str')
                final_df['file_path'] = final_df['file_path'].astype('str')
                final_df['page_content'] = final_df['page_content'].apply(lambda x:clean_text(x))
                
                output_dir_path = output_directory + directory_name + '/'
                utility.output_dir_handling(output_dir_path)
                output_file_name = output_dir_path+directory_name+".csv" 
                final_df.to_csv(output_file_name, index=False)

                chunk_df = extract_service.split_pages_to_content_chunks(final_df)
                chunk_output_file_name = output_dir_path+"/"+directory_name+"_chunk.csv"
                chunk_df.to_csv(chunk_output_file_name, index=False)

                project_code = api_data['project_code']
                directory_name_without_spaces = directory_name.replace(" ", "")
                index_name = project_code.lower()+"_"+directory_name_without_spaces.lower()+"_index"
                print("index_name", index_name)
                # dims = 1024
                # index_response = index_creation.creating_es_index(index_name, settings, es_client, dims)
                # print("index_response", index_response)
                # logging.info('index_response %s', index_response)
                
                # es_index = {
                #     "es_group_index": index_name,
                #     "group_name": directory_name,
                #     "output_file_path": output_dir_path,
                #     "chunk_output_file_name": chunk_output_file_name,
                #     "group_id": group_id,
                #     "doc_ids": doc_ids
                # }
                
                # group_index_list.append(es_index)
                # print("group_index_list", group_index_list)
                
                # if not index_response == "index creation failed":
                #     print("models_directory", models_directory)
                #     embedding_response = vector_embeddings_creation.create_vector_embeddings(chunk_output_file_name, index_name, models_directory, settings, es_client, embeddings, index_response)
                #     print("embedding_response", embedding_response)
                #     if embedding_response == "succeeded":
                #         print("send success response")
                #         logging.info('send success response')
                #         responseDict = utility.form_success_response(responseDict, "", "", "", api_data)
                #         print("responseDict", responseDict)
                #         logging.info('responseDict %s', responseDict)
                #         responseDict["group_index_names"] = group_index_list
                        
                #         # send message only on last folder
                #         if len(directory_names)==number_of_folders:
                #             utility.publish_results(channel, responseDict, project_code, settings, connection)
                #     else:
                #         print("send failure response")
                #         logging.info('send failure response')
                #         responseDict = utility.form_error_response(responseDict, "documents upload to elasticsearch failed", api_data, filename_pdf)
                #         responseDict["group_index_names"]=[]
                #         print("responseDict", responseDict)
                #         logging.info('responseDict %s', responseDict)

                #         # send message only on last folder
                #         if len(directory_names)==number_of_folders:
                #             utility.publish_results(channel, responseDict, project_code, settings, connection)
                # else:
                #     print("Failure")
                #     logging.info('Failure')
                #     responseDict = utility.form_error_response(responseDict, "elasticsearch index creation failed", api_data, filename_pdf)
                #     responseDict["group_index_names"]=[]
                #     print("responseDict", responseDict)
                #     logging.info('responseDict %s', responseDict)
                #     #send message only on last folder
                #     if len(directory_names)==number_of_folders:
                #         utility.publish_results(channel, responseDict, project_code, settings, connection)
            else:
                output_dir_path = output_directory + directory_name + '/'
                utility.output_dir_handling(output_dir_path)
                print("No Need to train this group name")
        utility.publish_results(channel, responseDict, project_code, settings, connection)
        print("SUCCESSFULL")   
    except Exception as e:
        responseDict = {}
        job_date = datetime.datetime.now()
        responseDict["job_date"] = str(job_date)
        project_code = api_data['project_code']
        responseDict = utility.form_error_response(responseDict, str(e), api_data, "")
        responseDict["group_index_names"]=[]
        utility.publish_results(channel, responseDict, project_code, settings, connection) 
        
     
def clean_text(text):
    #Remove non ASCII characters 
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = text.lower()
    #replace multiple new lines with one new line
    text= re.sub(r"\n+", "\n", text).strip() 
    #replace extra spaces with single space
    text= re.sub(' +',' ',text)
    return text