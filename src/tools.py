from elasticsearch import Elasticsearch

client = Elasticsearch(hosts="http://localhost:9200")


def list_aliases():
    response = client.indices.get_alias(index="*", expand_wildcards="open")
    return [name for name in response.body]
