from flask import Flask, request, jsonify, make_response
import json, os, config
import hashlib
import time
from collections import defaultdict
from engine.ks_postprocessing import es2rasa
from engine.ks_handler import ks_elastic_search
from engine.embedding_model import Embedding
from flask_cors import CORS 
from elasticsearch import Elasticsearch

from engine import prompt_template 
from engine import load_llm

llm_chain= prompt_template.create_prompt_template()
llm=load_llm.llm_pipeline()

app = Flask(__name__)
CORS(app)

custom_env = "local"
# custom_env = os.environ.get('custom_env')
settings = (config.settings[custom_env])
app.config.from_object(settings)

base_url            = app.config['BASEURL']
port_number         = app.config['PORT']
elasticsearch_url   = app.config['ELASTICSEARCH_URL']
ks_files_endpoint   = app.config['KS_FILES_ENDPOINT']
url_endpoint        = app.config['URL_ENDPOINT']
api_service         = app.config['API_SERVICE']

url_port = url_endpoint + str(port_number) + base_url + api_service
print("\n\n\nURL_PORT: ", url_port,'\n\n\n')

embeddings = Embedding(r'intfloat/e5-large-v2')
#embeddings = Embedding(r'/model/e5-large-v2')
es_client = Elasticsearch(elasticsearch_url)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': str(error)}), 404)

@app.route('/', methods=['GET'])
def intro():
    return "Welcome to the KS inference microservice"

@app.route(base_url+api_service, methods=['POST'])
def process_query():
    try:
        # Load JSON data from request
        print("Inside ks_process_query")

        request_data = request.get_json()

        if isinstance(request_data, str):
            request_data = json.loads(request_data)

        # Extract required fields from JSON
        query = request_data.get('query', '')
        index = request_data.get('index', '')
        ks_accuracy = float(request_data.get('ks_accuracy', 0.0))

        print(query, index, ks_accuracy)

        #print("ES_Client", es_client)

        # Perform elastic search
        hits = ks_elastic_search(query, index, embeddings, es_client)

        #print("Hits", hits)

        docs_list = []

        for rec in hits['hits']:
            dic={'page_content':rec['_source']['content'],'source':rec['_source']['source'], 'page_id': rec['_source']['page_id']}
            filepath = rec['_source']['file_path']
            full_path = ks_files_endpoint + filepath
            full_path = full_path.replace("..","")
            full_path = full_path.replace("/files_local/", "")
            full_path = full_path.replace("/files_int/","")
            full_path = full_path.replace("/files_prod/","")
            rec['_source'].update({'file_path':full_path})
            docs_list.append(dic)
    
        ## Ask Local LLM context informed prompt
        ct=docs_list[0]['page_content']

        formatted_prompt=llm_chain.format(context=ct,query=query,response=llm(ct))
        if "answer:" in formatted_prompt:
            answer = formatted_prompt.split(sep="answer:")[1]
        else:
            answer = formatted_prompt
        print("formatted output\n",answer)

        # Convert hits to response_json format
        response_json = {
            "hits": hits
            # Add other fields as needed
        }
        # # Serializing json
        # json_object = json.dumps(response_json, indent=4)
        
        # # Writing to sample.json
        # with open("hits_resp.json", "w") as outfile:
        #     outfile.write(json_object)

        # Generate Rasa message
        matches, dctMessage = es2rasa(response_json['hits'], ks_accuracy, answer, ks_files_endpoint)

        dct_raw = response_json['hits']
        dct_raw['hits'][0]['summary'] = answer

        #carousel first response as summary
        dctMessage['payload']['elements'][0]['subtitle'] = answer
        # print("dctMessage", dctMessage)

        # Construct and return the final response
        response = {
            "matches": matches,
            # "summary": answer,
            "dct_raw": dct_raw,
            "dctMessage": dctMessage
            # Add other fields as needed
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port_number, debug=True, use_reloader=False)