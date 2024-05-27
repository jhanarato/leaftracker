import pytest

from leaftracker.adapters.elastic_index import Index
from leaftracker.adapters.elastic_repository import SpeciesRepository, SPECIES_MAPPING


@pytest.fixture
def repository() -> SpeciesRepository:
    index = Index("test_species", SPECIES_MAPPING)
    repo = SpeciesRepository(index=index)
    repo.index.delete_all_documents()
    return repo


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
