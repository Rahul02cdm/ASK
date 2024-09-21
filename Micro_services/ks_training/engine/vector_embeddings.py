import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
import elasticsearch
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm
tqdm.pandas()
import os
import logging
#from engine.embedding_model import embeddings
import engine.create_index as index_creation

class Tokenizer(object):
    def __init__(self, models_directory):
        self.model = SentenceTransformer(models_directory)

    def get_token(self, documents):
        sentences  = [documents]
        sentence_embeddings = self.model.encode(sentences)
        encod_np_array = np.array(sentence_embeddings)
        encod_list = encod_np_array.tolist()
        return encod_list[0]
    

def create_vector_embeddings(input_file_path, index_name, models_directory, settings, es_client, embeddings, index_response):
    try:
        final_df = pd.read_csv(input_file_path, encoding='utf-8')

        last_id = None
        if index_response == "index aleady exists":
            files_name = final_df["source"].unique()
            index_creation.delete_es_document(index_name, files_name, es_client)
            print("Cleared doc memory")
            last_id = index_creation.find_last_id(index_name, es_client)
        
        final_df['content_vector'] = final_df['content'].progress_apply(lambda x: embeddings.embed_documents(x))
        
        indices = [index_name]
        dflist = [final_df]
           
        #converting text into vectors of size 382
        # token_instance = Tokenizer(models_directory)
        # final_df['page_content_vector'] = final_df['page_content'].progress_apply(token_instance.get_token)

        for index_name, dataframe in zip(indices, dflist):
            print("index_name", index_name)
            logging.info('index_name %s', index_name)
            
            for i, row in dataframe.iterrows():
                if not last_id == None:
                    i = last_id + i
                print("create_vector_embeddings ", i)
                logging.info('create_vector_embeddings  %s', i)
                #print(type(row["vector"]))
                # doc = {
                #     "doc_id": row["doc_id"],
                #     "doc_title": row["doc_title"],
                #     "page_id": row["page_id"],
                #     "page_content": row["page_content"],
                #     "page_content_vector": row["page_content_vector"],
                #     "file_path": row["file_path"]
                # }
                doc = {
                    "sid": int(i),
                    "content_id": str(row["content_id"]),
                    "source": row["source"],
                    "page_id": row["page_id"],
                    "content": row["content"],
                    "content_vector": row["content_vector"],
                    "file_path": row["file_path"]
                }
                es_client.index(index=index_name, id=i, document=doc)
            return "succeeded"
    except Exception as e:
        print("Exception", str(e))
        logging.info('Exception  %s', str(e))
        return "failed"