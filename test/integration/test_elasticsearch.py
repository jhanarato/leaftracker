import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elasticsearch import DocumentStore, Document, Lifecycle

INDEX_NAME = "test_index"
MAPPINGS = {"properties": {"content": {"type": "text"}}}


def delete_test_indexes():
    client = Elasticsearch(hosts="http://localhost:9200")
    aliases = client.indices.get_alias(index="test_*")
    for alias in aliases:
        client.options(ignore_status=404).indices.delete(index=alias)


@pytest.fixture(autouse=True, scope='session')
def test_indexes():
    yield
    delete_test_indexes()


@pytest.fixture
def lifecycle() -> Lifecycle:
    lc = Lifecycle(INDEX_NAME, MAPPINGS)
    lc.delete()
    lc.create()
    yield lc
    lc.delete()


@pytest.fixture
def store() -> DocumentStore:
    return DocumentStore(INDEX_NAME)


@pytest.fixture
def document() -> Document:
    return Document(
        document_id="some-doc",
        source={"content": "some content"}
    )


class TestLifecycle:
    def test_create_when_missing(self, lifecycle):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()

    def test_dont_overwrite_existing_index_on_create(self, lifecycle, store, document):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()
        reference = store.add(document)
        lifecycle.create()
        retrieved = store.get(reference)
        assert retrieved.document_id == reference

    def test_no_error_on_delete_twice(self, lifecycle):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.delete()
        assert not lifecycle.exists()
        

class TestDocumentStore:
    def test_should_delete_documents(self, lifecycle, store, document):
        store.add(document)
        lifecycle.refresh()
        assert store.count() == 1
        store.delete_all()
        lifecycle.refresh()
        assert store.count() == 0

    def test_should_allow_delete_documents_when_empty(self, lifecycle, store):
        store.delete_all()
        lifecycle.refresh()
        assert store.count() == 0
        store.delete_all()
        lifecycle.refresh()
        assert store.count() == 0

    def test_should_indicate_missing_document(self, store):
        assert not store.exists("not-a-doc")

    def test_should_confirm_document_exists(self, lifecycle, store, document):
        store.add(document)
        lifecycle.refresh()
        assert store.exists(document.document_id)


class TestConsistency:
    def test_get_is_immediately_consistent(self, store, document):
        document_id = store.add(document)
        retrieved = store.get(document_id)
        assert document == retrieved

    def test_exists_is_immediately_consistent(self, store, document):
        document_id = store.add(document)
        assert store.exists(document_id)

    def test_count_requires_refresh_to_be_consistent(self, lifecycle, store, document):
        store.add(document)
        assert store.count() == 0
        lifecycle.refresh()
        assert store.count() == 1

    def test_must_refresh_index_before_delete_all_is_consistent(self, lifecycle, store, document):
        document_id = store.add(document)
        store.delete_all()
        assert store.exists(document_id)

        lifecycle.refresh()
        store.delete_all()
        assert not store.exists(document_id)
