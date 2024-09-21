import os, glob, sys, json, datetime, shutil
import pika
import pika.exceptions
import elasticsearch
from elasticsearch import Elasticsearch

def form_success_response(responseDict, filename_pdf, output_path, output_filepaths, api_data):
    zid = api_data['zid']
    sub_service = api_data['sub_service']
    project_code = api_data['project_code']
    responseDict["service"] = "chap"
    responseDict["sub_service"] = sub_service
    responseDict["project_code"] = project_code
    #responseDict["file_name"] = filename_pdf
    #responseDict["file_path_output"] = output_path
    responseDict["process_status"] = "success"
    responseDict["zid"] = zid
    job_date = datetime.datetime.now()
    responseDict["job_date"] = str(job_date)
    responseDict["category"] = "data_preparation"
    #responseDict["output_filepath"] = output_filepaths
    return responseDict

def form_error_response(responseDict, err_msg, api_data, filename_pdf):
    zid = api_data['zid']
    sub_service = api_data['sub_service']
    project_code = api_data['project_code']
    responseDict["process_status"] = "failed"
    responseDict["service"] = "chap"
    responseDict["sub_service"] = sub_service
    responseDict["project_code"] = project_code
    responseDict["error_msg"] = err_msg
    responseDict["zid"] = zid
    responseDict["file_path_output"] = "null"
    responseDict["file_name"] = filename_pdf
    responseDict["category"] = "data_preparation"
    return responseDict

def publish_results(channel, responseDict, project_code, settings, connection):
    print(" [x] Sent %r" % (channel))
    if responseDict["category"] == "pdf_convert":
        routing_key = settings.BASE_TOPIC+".pdf_convert.be.response"
    else:
        routing_key = settings.BASE_TOPIC+"."+settings.SUB_TOPIC+".be.response"
    message = json.dumps(responseDict)
    try:
        if not connection or connection.is_closed:
            channel, connection = establish_socket_connection(settings)
        channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)
        print(" [x] Sent %r:%r" % (routing_key, message))
    # except Exception as error:
    #     return "connection failed"
    except pika.exceptions.ConnectionClosed as e:
        print("Exception %s", str(e))
        return "connection failed"

      
def select_folder_dir(api_data, settings):
    # zid = api_data['zid']
    # sub_service = api_data['sub_service']
    project_code = api_data['project_code']
    input_directory = settings.VOLUME_MOUNT+"/"+project_code+"/ks/input/"
    output_directory = settings.VOLUME_MOUNT+"/"+project_code+"/ks/output/"
    op_dir_and_ip_dir_image = settings.VOLUME_MOUNT+"/"+project_code+"/ks/opandip_image/"
    output_directory_hf = settings.VOLUME_MOUNT+"/"+project_code+"/ks/output_hf_removal/"
    output_dir_singleimage = settings.VOLUME_MOUNT+"/"+project_code+"/ks/output_hf_singleimage/"
    models_directory = settings.VOLUME_MOUNT+"/Models/e5-large-v2"
    logger_directory = settings.VOLUME_MOUNT+"/"+project_code+"/ks/logs/"
    return input_directory, output_directory, op_dir_and_ip_dir_image, output_directory_hf, models_directory, logger_directory, output_dir_singleimage
       
def output_dir_handling(output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    else:
        files = glob.glob(output_path+'/*')
        for f in files:
            os.remove(f)
            
def logger_dir_handling(logger_path):
    if not os.path.exists(logger_path):
        os.makedirs(logger_path)
            
def establish_socket_connection(settings):
    try:
        credentials = pika.PlainCredentials(settings.MQUSERNAME,settings.MQPASSWORD)
        #host = os.environ.get('AMQP_HOST')
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.MQHOST, port=settings.PORT, credentials= credentials, heartbeat=600, blocked_connection_timeout=300))
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host="host.docker.internal", port=5672, credentials= credentials))
        #connection = pika.BlockingConnection(pika.ConnectionParameters(host="35.222.86.83", port=7000, credentials= credentials))
        channel = connection.channel()
        channel.exchange_declare(exchange='topic_logs', exchange_type='topic', durable=True)
        return channel, connection
    except Exception as error:
        return "connection failed"
    
def establish_elasticsearch_connection(settings):
    try:
        es_url = settings.ELASTICSEARCH_URL
        es_client = Elasticsearch(es_url)
        es_client.info()
        # Create the client instance
        # client = Elasticsearch(
        #     "https://localhost:9200",
        #     ca_certs="/path/to/http_ca.crt",
        #     basic_auth=("elastic", ELASTIC_PASSWORD)
        # )
        return es_client
    except Exception as error:
        return "connection failed"