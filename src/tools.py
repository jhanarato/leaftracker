from elasticsearch import Elasticsearch

client = Elasticsearch(hosts="http://localhost:9200")


def list_aliases():
    response = client.indices.get_alias(index="*", expand_wildcards="open")
    return [name for name in response.body]


def list_test_aliases():
    es = Elasticsearch(hosts="http://localhost:9200")
    aliases = es.indices.get_alias(index="test_*")
    for alias in aliases:
        print(alias)


def delete_test_indexes():
    es = Elasticsearch(hosts="http://localhost:9200")
    aliases = es.indices.get_alias(index="test_*")
    for alias in aliases:
        es.options(ignore_status=404).indices.delete(index=alias)
