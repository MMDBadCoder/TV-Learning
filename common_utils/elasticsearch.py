from elasticsearch import Elasticsearch

from TV_LEARNING.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_PROT


class ElasticConnectionFactory:
    __instance = None

    @staticmethod
    def get_instance():
        if ElasticConnectionFactory.__instance is None:
            ElasticConnectionFactory.__instance = ElasticConnectionFactory.create_new_connection()
        return ElasticConnectionFactory.__instance

    @staticmethod
    def create_new_connection():
        nodes = [
            {
                'host': ELASTICSEARCH_HOST,
                'port': ELASTICSEARCH_PROT,
                "scheme": "http"
            }
        ]
        return Elasticsearch(nodes)
