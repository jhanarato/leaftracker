import pytest

from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.adapters.elastic import Index
from leaftracker.domain.model import Species, ScientificName
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


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
def added_species(species_index, species) -> Species:
    uow = ElasticUnitOfWork()

    with uow:
        uow.species().add(species)
        uow.commit()

    return species


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

    def test_should_indicate_missing_document(self, species_index):
        assert not species_index.document_exists("missing-species-reference")

    def test_should_confirm_document_exists(self, species_index, added_species):
        assert species_index.document_exists(added_species.reference)


@pytest.fixture
def species() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )
    )


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_queue_documents_to_commit(self, repository, species):
        repository.add(species)
        assert len(repository.queued()) == 1

    def test_should_clear_queue(self, repository, species):
        repository.add(species)
        repository.clear_queue()
        assert not repository.queued()


class TestElasticUnitOfWork:
    def test_should_rollback_if_not_committed(self, species):
        uow = ElasticUnitOfWork()
        uow.species().index.delete_all_documents()
        uow.species().index.refresh()

        with uow:
            uow.species().add(species)

        assert species.reference is None

    def test_should_commit(self, species):
        uow = ElasticUnitOfWork()
        uow.species().index.delete_all_documents()
        uow.species().index.refresh()

        with uow:
            uow.species().add(species)
            uow.commit()

        assert species.reference is not None
