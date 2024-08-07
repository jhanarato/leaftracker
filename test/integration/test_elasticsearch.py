import pytest

from leaftracker.adapters.elastic.elasticsearch import DocumentStore, Document, Lifecycle

INDEX_NAME = "test_index"
MAPPINGS = {"properties": {"content": {"type": "text"}}}


@pytest.fixture
def lifecycle():
    lc = Lifecycle(INDEX_NAME, MAPPINGS)
    yield lc
    lc.delete()


@pytest.fixture
def store(lifecycle):
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
        assert not lifecycle.exists()
        lifecycle.create()
        assert lifecycle.exists()

    def test_dont_overwrite_existing_index_on_create(self, lifecycle, store, document_with_id):
        lifecycle.create()
        reference = store.add(document_with_id)
        lifecycle.create()
        retrieved = store.get(reference)
        assert retrieved.document_id == reference

    def test_deleting_missing_index(self, lifecycle):
        assert not lifecycle.exists()
        lifecycle.delete()
        assert not lifecycle.exists()


class TestDocumentStore:
    def test_add_new_without_id(self, store, document_without_id):
        document_id = store.add(document_without_id)
        assert store.exists(document_id)

    def test_add_new_with_id(self, store, document_with_id):
        existing_id = document_with_id.document_id
        added_id = store.add(document_with_id)
        assert existing_id == added_id
        retrieved = store.get(existing_id)
        assert retrieved.document_id == existing_id

    def test_get_existing(self, store, document_with_id):
        store.add(document_with_id)
        retrieved = store.get(document_with_id.document_id)
        assert retrieved == document_with_id

    def test_get_missing(self, store):
        assert store.get("no-such-doc") is None

    def test_doesnt_exist(self, store):
        assert not store.exists("not-a-doc")

    def test_does_exist(self, store, document_with_id):
        store.add(document_with_id)
        assert store.exists(document_with_id.document_id)

    def test_update_existing(self, store, document_without_id):
        store.add(document_without_id)
        assert document_without_id.source["content"] == "some content"

        document_without_id.source["content"] = "new content"
        reference = store.add(document_without_id)

        retrieved = store.get(reference)
        assert retrieved.source["content"] == "new content"
