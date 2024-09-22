# -*- coding: utf-8 -*-
import os

class Config:
    # project root directory
    #BASE_DIR = os.path.join(os.pardir, os.path.dirname(__file__))

    # Flask Configuration
    # --------------------------------------------------------------------
    DEBUG = False
    TESTING = False

class IntegrationConfig(Config):
    ENV = os.environ.get("integration")
    DEBUG = True
    HOST = "0.0.0.0"
    BASEURL = "/int/api/v1/"
    PORT = 6003
    VOLUME_MOUNT = "/files_int"
    ELASTICSEARCH_URL = "http://34.93.169.79:9200"
    KS_FILES_ENDPOINT="http://34.93.169.79:5001/static/"
    URL_ENDPOINT = "http://34.93.169.79:"
    API_SERVICE = "ks_process_query"

class ProductionConfig(Config):
    ENV = os.environ.get("production")
    DEBUG = False
    HOST = "0.0.0.0"
    BASEURL = "/prod/api/v1/"
    PORT = 6003
    VOLUME_MOUNT = "/files_prod"
    ELASTICSEARCH_URL = "http://10.244.2.211:9200"
    KS_FILES_ENDPOINT="http://10.244.2.211:7072/static/"
    URL_ENDPOINT = "http://10.244.2.211:"
    API_SERVICE = "ks_process_query"

class LocalConfig(Config):
    ENV = os.environ.get("local")
    DEBUG = True
    HOST = "0.0.0.0"
    BASEURL = "/local/api/v1/"
    PORT = 6003
    VOLUME_MOUNT = "C:/Users/rahul/OneDrive/With_Inside/2024/ASK/files_local"   #"../files_local"
    ELASTICSEARCH_URL = "http://localhost:9200"
    KS_FILES_ENDPOINT="http://localhost:5001/static/"
    URL_ENDPOINT = "http://localhost:"
    API_SERVICE = "ks_process_query"

settings = {
    'local': LocalConfig,
    'integration': IntegrationConfig,
    'production': ProductionConfig,
    'default': ProductionConfig,
}