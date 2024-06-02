import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elastic_repository import SpeciesRepository, SPECIES_INDEX


@pytest.fixture
def repository() -> SpeciesRepository:
    repo = SpeciesRepository(INDEX_TEST_PREFIX + SPECIES_INDEX)
    repo.index.delete_all_documents()
    return repo


class TestSpeciesRepository:
    def test_should_indicate_missing_document(self, repository):
        assert repository.get("Nothing") is None

    def test_should_queue_documents_to_commit(self, repository, saligna):
        repository.add(saligna)
        assert len(repository.added()) == 1

    def test_should_clear_queue(self, repository, saligna):
        repository.add(saligna)
        repository.clear_added()
        assert not repository.added()
