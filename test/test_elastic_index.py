import pytest

from leaftracker.adapters.elasticsearch import Index, Document, Lifecycle

INDEX_NAME = "test_prefix"
MAPPINGS = {"properties": {"content": {"type": "text"}}}


@pytest.fixture
def lifecycle() -> Lifecycle:
    return Lifecycle(INDEX_NAME, MAPPINGS)


@pytest.fixture
def index() -> Index:
    return Index(INDEX_NAME)


@pytest.fixture
def document() -> Document:
    return Document(
        document_id="some-doc",
        source={"content": "some content"}
    )


class TestIndex:
    def test_should_delete_documents(self, lifecycle, index, document):
        index.add_document(document)
        lifecycle.refresh()
        assert index.document_count() == 1
        index.delete_all_documents()
        lifecycle.refresh()
        assert index.document_count() == 0

    def test_should_allow_delete_documents_when_empty(self, lifecycle, index):
        index.delete_all_documents()
        lifecycle.refresh()
        assert index.document_count() == 0
        index.delete_all_documents()
        lifecycle.refresh()
        assert index.document_count() == 0

    def test_should_indicate_missing_document(self, index):
        assert not index.document_exists("not-a-doc")

    def test_should_confirm_document_exists(self, lifecycle, index, document):
        index.add_document(document)
        lifecycle.refresh()
        assert index.document_exists(document.document_id)


@pytest.mark.skip("Slow tests.")
class TestLifecycle:
    def test_should_create_and_delete_indexes(self, lifecycle, index):
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

    def test_should_skip_creation_when_exists(self, lifecycle, index, document):
        index.add_document(document)
        lifecycle.refresh()
        assert index.document_count() == 1
        lifecycle.create()
        assert index.document_count() == 1
