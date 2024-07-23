from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.adapters.elasticsearch import DocumentStore, Document
from leaftracker.domain.model import Species


class TestElasticSpeciesRepository:
    def test_add_to_elasticsearch_index(self):
        species = Species(current_name="Machaerina juncea", reference="species-0001")
        species.taxon_history.add_previous_name("Baumea juncea")
        store = DocumentStore("test_integration_species")
        repository = ElasticSpeciesRepository(store)
        repository.add(species)
        repository.commit()
        document = store.get(species.reference)
        assert document == Document(
            document_id="species-0001",
            source={
                "current_scientific_name": "Machaerina juncea",
                "previous_scientific_names": ["Baumea juncea"]
            }
        )
