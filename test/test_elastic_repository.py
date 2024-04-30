from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName


class TestSpeciesRepository:
    def test_should_add_a_species(self):
        name = ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )

        species_in = Species("acacia-saligna", name)
        repo = SpeciesRepository()
        repo.add(species_in)

        es = Elasticsearch(hosts="http://localhost:9200")
        assert es.exists(index="species", id="acacia-saligna")
