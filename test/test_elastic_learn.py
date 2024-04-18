import pytest
from elasticsearch import Elasticsearch


@pytest.fixture
def client() -> Elasticsearch:
    es = Elasticsearch(hosts="http://localhost:9200")
    es.options(ignore_status=404).indices.delete(index="test_index")
    yield es


def test_should_create_document(client):
    doc = {
        'author': 'J.R.',
        'text': 'My very first document.',
    }

    response = client.create(index="test_index", document=doc, id="1")
    assert response.meta.status == 201
