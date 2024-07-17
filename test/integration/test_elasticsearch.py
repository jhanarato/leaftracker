import pytest
from elasticsearch import Elasticsearch, NotFoundError

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
def document_without_id():
    return Document(
        document_id=None,
        source={"content": "some content"}
    )


@pytest.fixture
def document_with_id() -> Document:
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

    def test_dont_overwrite_existing_index_on_create(self, lifecycle, store, document_with_id):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()
        reference = store.add(document_with_id)
        lifecycle.create()
        retrieved = store.get(reference)
        assert retrieved.document_id == reference

    def test_no_error_on_delete_twice(self, lifecycle):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.delete()
        assert not lifecycle.exists()


class TestDocumentStore:
    def test_add_new_document(self, store, document_without_id):
        document_id = store.add(document_without_id)
        assert store.exists(document_id)

    def test_get_existing_document(self, store, document_with_id):
        store.add(document_with_id)
        retrieved = store.get(document_with_id.document_id)
        assert retrieved == document_with_id

    def test_get_missing_document(self, store):
        with pytest.raises(NotFoundError):
            store.get("no-such-doc")

    def test_doesnt_exist(self, store):
        assert not store.exists("not-a-doc")

    def test_should_confirm_document_exists(self, store, document_with_id):
        store.add(document_with_id)
        assert store.exists(document_with_id.document_id)
