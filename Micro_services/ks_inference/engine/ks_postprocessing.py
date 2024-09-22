import requests
import logging
import json
from collections import defaultdict

def es2rasa(response_json, ks_accuracy, answer, ks_files_endpoint):
    num_found = int(response_json['total']['value'])

    if num_found < 1:
        matches = 0
        return (matches, None)


    dctMessage =  {"type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": []
                    }}

    lstDocNames = []
    lstScores = []
    lstPageNos = []
    lstPageContent = []
    lstRawPaths = []

    for doc_dict in response_json['hits']:
        source  = doc_dict['_source']['source']
        page    = doc_dict['_source']['page_id']
        lstDocNames.append(source)
        lstScores.append(doc_dict['_score'])
        lstPageNos.append(page)
        lstPageContent.append(doc_dict['_source']['content'])
        lstRawPaths.append(doc_dict['_source']['file_path'])
    index = 0
    for doc_name, score, page_no, page_content, file_path in zip(lstDocNames, lstScores, lstPageNos, lstPageContent, lstRawPaths):
    #for doc_name, score, page_no, page_content in zip(lstDocNames, lstScores, lstPageNos, lstPageContent):
        
        if float(score) > float(ks_accuracy):
            lstDicts = []
            my_path = ""
            #if "file_path" in locals():
            file_path = file_path.replace("..","")
            #my_path = ks_files_endpoint + file_path
            my_path = file_path
            my_path = my_path.replace("..","")
            my_path = my_path.replace("/files_int/","")
            my_path = my_path.replace("/files_prod","")
            my_path = my_path.replace("/files_local","")
            lstDicts.append({'title':'{0}'.format(str(page_no))+' ({:.0%})'.format(score), 'url': my_path, 'type':'web_url'})
            lstDicts.append({'title':u'\U0001F44D','type':'postback','payload':f'/submit_feedback{{"feedback":"yes","ks_carousel_index":{index}}}'})
            lstDicts.append({'title':u'\U0001F44E','type':'postback','payload':f'/submit_feedback{{"feedback":"no","ks_carousel_index":{index}}}'})
            index += 1

            if index >1:
                dctMessage["payload"]["elements"].append({
                        "title": doc_name,
                        # "subtitle": page_content[:500],
                        "subtitle": page_content,
                        "buttons": lstDicts
                        })
            elif index == 1:
               if answer: # for inference from ask-web
                   dctMessage["payload"]["elements"].append({
                        "title": doc_name,
                        "subtitle": answer[:500],
                        "buttons": lstDicts
                        })  
               elif not answer: # for inference from rasa
                    dctMessage["payload"]["elements"].append({
                        "title": doc_name,
                        "subtitle": page_content[:500],
                        "buttons": lstDicts
                        })     
    matches = len(dctMessage["payload"]["elements"])
    
    return (matches, dctMessage)

if __name__ == "__main__":
    es2rasa()
