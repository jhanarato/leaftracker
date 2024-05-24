import pytest

from leaftracker.adapters.elastic import Index
from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


@pytest.fixture
def saligna() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )
    )


@pytest.fixture
def dentifera() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Dentifera",
            is_most_recent=True
        )
    )


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo.index.create()
    repo.index.delete_all_documents()
    repo.index.refresh()
    return repo


@pytest.fixture
def species_index() -> Index:
    return SpeciesRepository().index


@pytest.fixture
def added_species(species_index, saligna) -> Species:
    uow = ElasticUnitOfWork()

    with uow:
        uow.species().add(saligna)
        uow.commit()

    return saligna


def test_repository_empty(repository):
    assert repository.index.document_count() == 0


class TestIndex:
    def test_should_create_missing_index(self, species_index):
        species_index.delete()
        assert not species_index.exists()
        species_index.create()
        assert species_index.exists()

    def test_should_not_overwrite(self, species_index, added_species):
        assert species_index.document_count() == 1
        species_index.create()
        assert species_index.document_count() == 1

    def test_should_delete_missing(self, species_index):
        species_index.delete()
        assert not species_index.exists()
        species_index.delete()
        assert not species_index.exists()

    def test_should_delete_existing(self, species_index):
        species_index.create()
        species_index.delete()
        assert not species_index.exists()

    def test_should_delete_documents(self, species_index, added_species):
        assert species_index.document_count() == 1
        species_index.delete_all_documents()
        species_index.refresh()
        assert species_index.document_count() == 0

    def test_should_allow_delete_documents_when_empty(self, species_index):
        species_index.delete_all_documents()
        assert species_index.document_count() == 0
        species_index.delete_all_documents()
        assert species_index.document_count() == 0

    def test_should_indicate_missing_document(self, species_index):
        assert not species_index.document_exists("missing-species-reference")

    def test_should_confirm_document_exists(self, species_index, added_species):
        assert species_index.document_exists(added_species.reference)


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_queue_documents_to_commit(self, repository, saligna):
        repository.add(saligna)
        assert len(repository.queued()) == 1

    def test_should_clear_queue(self, repository, saligna):
        repository.add(saligna)
        repository.clear_queue()
        assert not repository.queued()


@pytest.fixture
def uow() -> ElasticUnitOfWork:
    uow = ElasticUnitOfWork()
    uow.species().index.delete_all_documents()
    uow.species().index.refresh()
    return uow


class TestElasticUnitOfWork:
    def test_should_rollback_if_not_committed(self, uow, saligna):
        with uow:
            uow.species().add(saligna)

        assert saligna.reference is None

    def test_should_commit(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.commit()

        assert saligna.reference is not None

    def test_should_add_two_species(self, uow, saligna, dentifera):
        with uow:
            uow.species().add(saligna)
            uow.species().add(dentifera)
            uow.commit()

        assert uow.species().index.document_count() == 2

    def test_should_clear_queue_on_rollback(self, uow, saligna):
        with uow:
            uow.species().add(saligna)

        assert not uow.species().queued()

    def test_should_rollback_explicitly(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.rollback()
            assert not uow.species().queued()

    def test_should_clear_queue_after_commit(self, uow, saligna):
        with uow:
            uow.species().add(saligna)
            uow.commit()
            assert not uow.species().queued()


class TestTestIndicies:
    def test_should_normally_use_production_index(self):
        uow = ElasticUnitOfWork(use_test_indexes=False)
        assert uow.species().index.name == "species"

    def test_should_use_test_index(self):
        uow = ElasticUnitOfWork(use_test_indexes=True)
        assert uow.species().index.name == "test_species"

    def test_should_recreate_test_index(self, saligna):
        uow = ElasticUnitOfWork(use_test_indexes=True)

        with uow:
            uow.species().add(saligna)
            uow.commit()

        new_uow = ElasticUnitOfWork(use_test_indexes=True)
        assert new_uow.species().index.document_count() == 0
