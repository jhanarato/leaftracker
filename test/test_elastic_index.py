import pytest

from leaftracker.adapters.elastic_index import Index, Document


@pytest.fixture
def index() -> Index:
    return Index(
        name="test_index",
        mappings={
            "properties": {
                "content": {"type": "text"}
            }
        }
    )


@pytest.fixture
def document() -> Document:
    return Document(
        document_id="some-doc",
        source={"content": "some content"}
    )


class TestIndex:
    def test_should_create_and_delete_indexes(self, index):
        index.delete()
        assert not index.exists()
        index.create()
        assert index.exists()
        index.create()
        assert index.exists()
        index.delete()
        assert not index.exists()
        index.delete()
        assert not index.exists()

    def test_should_not_overwrite(self, index, document):
        index.add_document(document)
        index.refresh()
        assert index.document_count() == 1
        index.create()
        assert index.document_count() == 1

    def test_should_delete_documents(self, index, document):
        index.add_document(document)
        index.refresh()
        assert index.document_count() == 1
        index.delete_all_documents()
        index.refresh()
        assert index.document_count() == 0

    def test_should_allow_delete_documents_when_empty(self, index):
        index.delete_all_documents()
        assert index.document_count() == 0
        index.delete_all_documents()
        assert index.document_count() == 0

    def test_should_indicate_missing_document(self, index):
        assert not index.document_exists("not-a-doc")

    def test_should_confirm_document_exists(self, index, document):
        index.add_document(document)
        index.refresh()
        assert index.document_exists(document.document_id)
