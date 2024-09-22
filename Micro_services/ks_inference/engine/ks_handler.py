import requests
import json
import logging
import hashlib
import time
import requests
from requests.structures import CaseInsensitiveDict
import numpy as np
import pandas as pd
import json
import engine.embedding_model
from sentence_transformers import SentenceTransformer, util

def ks_elastic_search(query, index, es_embeddings, es_client):
    token_vector = es_embeddings.embed_documents(query)
    query={ "knn"   : 
                { "field" : "content_vector" ,
                  "query_vector" : token_vector,
                   "k" : 5,
                   "num_candidates" : 20 
                } ,
         "_source" : [ "source" , "page_id", "content", "file_path"] }

    res = es_client.search(index=index, body=query)
    hits = res['hits']
    return hits
