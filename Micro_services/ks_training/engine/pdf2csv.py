import tika
from tika import parser
import numpy as np
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter

#Extract page wise data from document 
def tika_ocr_individual_files(file_index, file_path, filename_pdf, unwanted_pages_list, settings):
    page_data=[]
    tika_server_url = settings.TIKA_SERVER_URL
    raw_xml = parser.from_file(file_path, tika_server_url, xmlContent=True, requestOptions={'timeout': 300})
    body = raw_xml['content'].split('<body>')[1].split('</body>')[0]
    body_without_tag = body.replace("<p>", "").replace("</p>", "").replace("<div>", "").replace("</div>","").replace("<p />","")
    text_pages = body_without_tag.split("""<div class="page">""")[1:]
    num_pages = len(text_pages)
    tp=num_pages+1
    page_id=list(range(1, tp))
    
    for page_id, page_content in zip(page_id, text_pages):
        if len(unwanted_pages_list)>0:
            if (page_id not in unwanted_pages_list):
                custom_file_path = file_path+"#page="+str(page_id)
                page_data.append({"doc_id":file_index, "doc_title":filename_pdf, "page_id":page_id, "page_content":page_content, "file_path": custom_file_path})
        else:
            custom_file_path = file_path+"#page="+str(page_id)
            page_data.append({"doc_id":file_index, "doc_title":filename_pdf, "page_id":page_id, "page_content":page_content, "file_path": custom_file_path})
    return page_data


def split_pages_to_content_chunks(page_data):
    #Text splitter object 
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600,chunk_overlap=120,length_function=len)
    data = page_data
    #create data frame format 
    df = pd.DataFrame()
    cid = 0
    for i, row in data.iterrows():
        page_content = row["page_content"]
        file_path = row["file_path"]
        source = str(row["doc_title"])
        page_id = str(row["page_id"])
        cont_list = text_splitter.split_text(page_content)    

        for text in cont_list:
            cid = cid + 1
            entity = {'content_id':cid, 'source':source, 'page_id':page_id, 'content':text, 'file_path':file_path }
            df_dict = pd.DataFrame([entity])
            df = pd.concat([df,df_dict],ignore_index=True)
    return df