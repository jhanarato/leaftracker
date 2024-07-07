import pytest

from leaftracker.adapters.elasticsearch import DocumentStore, Document, Lifecycle

INDEX_NAME = "test_index"
MAPPINGS = {"properties": {"content": {"type": "text"}}}


@pytest.fixture
def lifecycle() -> Lifecycle:
    return Lifecycle(INDEX_NAME, MAPPINGS)


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
    def test_should_create_and_delete_indexes(self, lifecycle, store):
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()
        lifecycle.delete()
        assert not lifecycle.exists()
        lifecycle.delete()
        assert not lifecycle.exists()

    def test_should_skip_creation_when_exists(self, lifecycle, store, document):
        store.add(document)
        lifecycle.refresh()
        assert store.count() == 1
        lifecycle.create()
        assert store.count() == 1


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
