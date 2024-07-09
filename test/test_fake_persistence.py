import pytest

from conftest import FakeUnitOfWork, FakeSpeciesRepository
from fakes import FakeLifecycle, FakeDocumentStore
from leaftracker.adapters.elasticsearch import Document


class TestFakeUnitOfWork:
    def test_should_rollback_if_not_committed(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)

        assert saligna.reference is None

    def test_should_assign_reference_on_commit(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)
            uow.commit()

        assert saligna.reference == "species-0001"

    def test_should_retrieve_species_after_commit(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)
            uow.commit()

        retrieved = uow.species().get(saligna.reference)
        assert retrieved.reference == "species-0001"  # type: ignore

    def test_should_discard_uncommitted_species_on_rollback(self, saligna, dentifera):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)

        with uow:
            uow.species().add(dentifera)
            uow.commit()

        retrieved = uow.species().get("species-0001")
        assert retrieved.taxon_history.current().species == "dentifera"  # type: ignore


class TestFakeSpeciesRepository:
    def test_should_return_none_when_missing(self):
        assert FakeSpeciesRepository().get("missing") is None


class TestFakeLifecycle:
    def test_create_when_does_not_exist(self):
        lc = FakeLifecycle(exists=False)
        lc.create()
        assert lc.exists()

    def test_create_when_exists(self):
        lc = FakeLifecycle(exists=True)
        lc.create()
        assert lc.exists()

    def test_delete_when_does_not_exist(self):
        lc = FakeLifecycle(exists=False)
        lc.delete()
        assert not lc.exists()

    def test_delete_when_exists(self):
        lc = FakeLifecycle(exists=True)
        lc.delete()
        assert not lc.exists()


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
        assert retrieved.document_id == "species-0001"

    def test_id_preserved_when_adding(self):
        document = Document("a-unique-id", {"content": "some content"})
        store = FakeDocumentStore("species")
        reference = store.add(document)
        retrieved = store.get(reference)
        assert retrieved.document_id == "a-unique-id"
