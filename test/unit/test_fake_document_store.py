from fakes import FakeDocumentStore
from leaftracker.adapters.elastic.elasticsearch import Document


class TestFakeDocumentStore:
    def test_create_with_index_name(self):
        store = FakeDocumentStore("index-name")
        assert store.index() == "index-name"

    def test_add_creates_reference(self):
        document = Document(None, {"content": "some content"})
        store = FakeDocumentStore("species")
        reference = store.add(document)
        assert reference == "species-0001"

    def test_document_assigned_id_when_missing(self):
        document = Document(None, {"content": "some content"})
        store = FakeDocumentStore("species")
        reference = store.add(document)
        retrieved = store.get(reference)
        assert retrieved.document_id == "species-0001"  # type: ignore

    def test_id_preserved_when_adding(self):
        document = Document("a-unique-id", {"content": "some content"})
        store = FakeDocumentStore("species")
        reference = store.add(document)
        retrieved = store.get(reference)
        assert retrieved.document_id == "a-unique-id"  # type: ignore
