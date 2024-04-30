import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def acacia_species() -> Species:
    name = ScientificName(
        genus="Acacia",
        species="Saligna",
        is_most_recent=True
    )

    return Species("acacia-saligna", name)


@pytest.fixture
def slow_refresh() -> None:
    es = Elasticsearch(hosts="http://localhost:9200")
    es.indices.put_settings(
        index="species",
        settings={
            "refresh_interval": "60s"
        }
    )
    yield
    es.indices.put_settings(
        index="species",
        settings={
            "refresh_interval": "1s"
        }
    )


class TestSpeciesRepository:
    def test_should_add_a_species(self, acacia_species):
        es = Elasticsearch(hosts="http://localhost:9200")
        assert es.indices.exists(index="species")
        es.delete(index="species", id=acacia_species.reference)

        repo = SpeciesRepository()
        repo.add(acacia_species)

        assert es.exists(index="species", id="acacia-saligna")

    def test_should_get_a_species(self, acacia_species, slow_refresh):
        repo = SpeciesRepository()
        repo.add(acacia_species)
        species = repo.get(acacia_species.reference)
        assert species == acacia_species
