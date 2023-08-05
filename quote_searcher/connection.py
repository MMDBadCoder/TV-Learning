from elasticsearch import Elasticsearch

from TV_LEARNING.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_PROT


class ConnectionFactory:
    __instance = None

    @staticmethod
    def get_instance():
        if ConnectionFactory.__instance is None:
            ConnectionFactory.__instance = ConnectionFactory.create_new_connection()
        return ConnectionFactory.__instance

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
