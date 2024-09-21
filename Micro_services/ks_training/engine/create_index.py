from elasticsearch import Elasticsearch
import logging
import shutil, os
import engine.utils as utility

def creating_es_index(index_name, settings, es_client, dims):
    try:
        config = { 
            "mappings": {
                "properties": { "content_vector": {
                                 "type":"dense_vector",
                                 "dims":dims,       # 1024 | 768
                                 "index":True,
                                 "similarity":"cosine" },
                 "sid":{"type":"integer"} ,
                 "content_id": {"type":"text"}, #integer
                 "source": {"type":"text"},
                 "page_id": {"type":"text"},
                 "content" : {"type":"text"},
                 "file_path": {"type":"text"}
                }
            }
        }
        
        #create the index once run the code one time 
        if not es_client.indices.exists(index=index_name):
            print("Creating index "+index_name)
            logging.info('Creating index %s', index_name)
            es_client.indices.create(index=index_name, mappings=config["mappings"])
            return "index created successfully"
        else:
            print(index_name+" index aleady exists")
            logging.info('index aleady exists  %s', index_name)
            # es_client.delete_by_query(index=index_name, body={"query": {"match_all": {}}})
            return "index aleady exists"
    except Exception as e:
        print("Exception", str(e))
        logging.info('Exception  %s', str(e))
        return "index creation failed"

def delete_es_index(index, es_client):
    try:
        response=es_client.indices.get_alias(index=index)
        if(len(response)>0):
            for index in response:
                # print("index", index)
                delete_response=es_client.indices.delete(index=index)
                print(delete_response)
        else:
            print("Indices Not found")
    except Exception as e:
        print(str(e))

def delete_es_document(index, files_name, es_client):
    try:
        for filename in files_name:
            query = {"query": {"match_phrase": {"source": filename}}}
            response = es_client.delete_by_query(index=index, body=query)
            resp = response['deleted']
            if resp > 0:
                print("Documents deleted")
            else:
                print("No Documents found")
    except Exception as e:
        print(str(e))

def find_last_id(index_name, es_client):
    try:
        es_client.indices.refresh(index=index_name)
        # es_client.cluster.put_settings(body={"persistent": {"indices.id_field_data.enabled": True}})
        response = es_client.search(index=index_name,
                            body={"size": 1,
                                "sort": [{"sid": {"order": "desc"}}]})
        last_id = response['hits']['hits'][0]['_id'] if response['hits']['hits'] else None
        print("last_id", last_id)
        if last_id == None:
            return(None)
        else:
            last_id = int(last_id) + 1
            return(last_id)
    except Exception as e:
        return(str(e))


def delete_es(api_data, es_client, settings):
    project_code = api_data['project_code']
    delete_type = api_data['delete_type']
    if delete_type == 'project':
        index = str(project_code) + '*'
        delete_es_index(index.lower(), es_client)
    elif delete_type == 'group':
        group_name = api_data['group_name']

        _, output_directory, _, _, _, _, _= utility.select_folder_dir(api_data, settings)
        grp_output_directory = output_directory + group_name
        if os.path.isdir(grp_output_directory):
            shutil.rmtree(grp_output_directory)
        index = str(project_code) + '_' + str(group_name) + '_index'
        delete_es_index(index.lower(), es_client)
    elif delete_type == 'files':
        group_name = api_data['group_name']
        files_name = api_data['files_name']
        index = str(project_code) + '_' + str(group_name) + '_index'
        delete_es_document(index.lower(), files_name, es_client)