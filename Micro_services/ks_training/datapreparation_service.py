import json, env_config, sys, os
import engine.init_training as training_service
import engine.utils as utility
from engine.embedding_model import Embedding
import engine.pdf2image_conversion as pdf_to_image
import engine.create_index as index_creation
import engine.multi_format as multi_format

# os.environ["http_proxy"] = 'http://z043398:Dean140298cdm@138.21.89.193:3128'
# os.environ["https_proxy"] = 'http://z043398:Dean140298cdm@138.21.89.193:3128'
# os.environ["HTTP_PROXY"] = 'http://z043398:Dean140298cdm@138.21.89.193:3128'
# os.environ["HTTPS_PROXY"] = 'http://z043398:Dean140298cdm@138.21.89.193:3128'
embeddings = Embedding(r'intfloat/e5-large-v2')

connection = None

def start_consumer_service(channel, settings, connection, es_client):

    # Declaration for be_topic_name
    be_queue_name = settings.QUEUE_NAME+"_"+settings.SUB_TOPIC+"_be_request"
    be_result = channel.queue_declare(be_queue_name, durable=True)
    print("be_result",be_result)
    be_queue_name = be_result.method.queue
    print("be_queue_name",be_queue_name)
    be_topic_name = settings.BASE_TOPIC+"."+settings.SUB_TOPIC+".be.request"
    # print("binding_key",be_topic_name)

    # Declaration for es_topic_name
    es_queue_name = settings.QUEUE_NAME+"_delete_be_request"
    es_result = channel.queue_declare(es_queue_name, durable=True)
    print("es_result",es_result)
    es_queue_name = es_result.method.queue
    print("es_queue_name",es_queue_name)
    es_topic_name = settings.BASE_TOPIC+".delete.be.request"
    # print("binding_key",es_topic_name)

    # Declaration for mf_topic_name
    mf_queue_name = settings.QUEUE_NAME+"_pdf_convert_be_request"
    mf_result = channel.queue_declare(mf_queue_name, durable=True)
    print("mf_result",mf_result)
    mf_queue_name = mf_result.method.queue
    print("mf_queue_name",mf_queue_name)
    mf_topic_name = settings.BASE_TOPIC+".pdf_convert.be.request"
    # print("binding_key",es_topic_name)

    channel.queue_bind(exchange='topic_logs', queue=be_queue_name, routing_key=be_topic_name)
    print(f' [*] Waiting for {be_topic_name} logs. To exit press CTRL+C')
    channel.queue_bind(exchange='topic_logs', queue=es_queue_name, routing_key=es_topic_name)
    print(f' [*] Waiting for {es_topic_name} logs. To exit press CTRL+C')
    channel.queue_bind(exchange='topic_logs', queue=mf_queue_name, routing_key=mf_topic_name)
    print(f' [*] Waiting for {mf_topic_name} logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        api_data = json.loads(body)
        print(" [x] %r:%r" % (method.routing_key, api_data))
        # client = credentials_init()
        # client1 = credentials_init1()
        
        if method.routing_key==be_topic_name:        
            if all(key in api_data for key in ('project_code', 'service', 'sub_service', 'zid', 'process_type', 'train_files', 'file_type')):
                print("All keys present")
                for_be_processing(channel, api_data, settings, connection, es_client, embeddings)
            else:
                print("keys not present")
                publish_be_results(channel, settings)
        elif method.routing_key==es_topic_name:
            if all(key in api_data for key in ('project_code', 'delete_type',)):
                print("All keys present")
                index_creation.delete_es(api_data, es_client, settings)
            else:
                print("keys not present")
                publish_be_results(channel, settings)
        elif method.routing_key==mf_topic_name:
            if all(key in api_data for key in ('project_code','group_name', 'files_name', 'sub_service')):
                print("All keys present")
                multi_format.multi_format_process(api_data, settings, channel, connection)
            else:
                print("keys not present")
                publish_mf_results(channel, settings)
    
    channel.basic_consume(queue=be_queue_name, on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue=es_queue_name, on_message_callback=callback, auto_ack=True)
    channel.basic_consume(queue=mf_queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    
def for_be_processing(channel, api_data, settings, connection, es_client, embeddings):
    result = training_service.extract_documets_data(channel, api_data, settings, connection, es_client, embeddings)
    return result
      
def publish_be_results(channel, settings):
    routing_key = settings.BASE_TOPIC+"."+settings.SUB_TOPIC+".be.response"
    message="Bad Request"
    channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)
    print(" [x] Sent %r:%r" % (routing_key, message))

def publish_mf_results(channel, settings):
    routing_key = settings.BASE_TOPIC+"."+settings.SUB_TOPIC+".be.response"
    message="Bad Request"
    channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)
    print(" [x] Sent %r:%r" % (routing_key, message))
    
if __name__ == '__main__':
    custom_env = 'local'
    # custom_env = os.environ.get('custom_env')
    print("custom_env", custom_env)
    settings = (env_config.settings[custom_env])
    print("BASE_TOPIC", settings.BASE_TOPIC)
    if (utility.establish_socket_connection(settings))=="connection failed":
        print("connection failed, pls check RabbitMQ server")
    else:
        if (utility.establish_elasticsearch_connection(settings))=="connection failed":
            print("connection failed, pls check Elasticsearch server")
        else:
            es_client = utility.establish_elasticsearch_connection(settings)
            channel, connection = utility.establish_socket_connection(settings)
            start_consumer_service(channel, settings, connection, es_client)