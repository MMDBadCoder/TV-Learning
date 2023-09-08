import json

from elasticsearch import Elasticsearch

from TV_LEARNING.settings import ELASTICSEARCH_HOST, ELASTICSEARCH_PROT
from common_utils.logging_utils import LoggerFactory


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


def validate_existence_of_elasticsearch_index():
    logger = LoggerFactory.get_instance()
    index_name = 'quotes'

    logger.info('Check existence of elasticsearch index')
    with ElasticConnectionFactory.create_new_connection() as es:
        if es.indices.exists(index=index_name):
            return True

        with open('quote_searcher/quotes_index_schema.json', 'r') as schema_file:
            schema = json.loads(''.join(schema_file.readlines()))

        # Create the index
        response = es.indices.create(index=index_name, body=schema)
        if response['acknowledged']:
            logger.info(f"Index '{index_name}' created successfully.")
            return True
        else:
            logger.info(f"Failed to create index '{index_name}'.")
            return False
