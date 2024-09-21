import os

class Config:
    DEBUG = False
    TESTING = False

class LocalConfig(Config):
    ENV = os.environ.get("local")
    DEBUG = True
    HOST = "0.0.0.0"
    BASE_TOPIC = "chap.dev.ks"
    SUB_TOPIC = "data_preparation"
    QUEUE_NAME = "chap_dev_ks"
    MQHOST = "localhost"
    MQUSERNAME = "guest"
    MQPASSWORD = "guest"
    PORT = 5672
    MQPUBLIC_PORT = "15672"
    VOLUME_MOUNT = "C:/Users/rahul/OneDrive/With_Inside/2024/ASK/files_local"
    # VOLUME_MOUNT = "../../../../files_local"
    TIKA_SERVER_URL = "http://localhost:9998/tika"
    ELASTICSEARCH_URL = "http://localhost:9200"

settings = {'local': LocalConfig}