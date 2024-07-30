from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.adapters.elasticsearch import DocumentStore, Document, Lifecycle
from leaftracker.domain.model import Species
from leaftracker.service_layer.elastic_uow import SPECIES_MAPPINGS, SPECIES_INDEX

INDEX_PREFIX = "test_integration_"


class TestElasticSpeciesRepository:
    def test_add_to_species_index(self):
        lifecycle = Lifecycle(INDEX_PREFIX + SPECIES_INDEX, SPECIES_MAPPINGS)
        lifecycle.create()

        species = Species(current_name="Machaerina juncea", reference="species-0001")
        species.taxon_history.add_previous_name("Baumea juncea")

        store = DocumentStore(INDEX_PREFIX + SPECIES_INDEX)
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

        lifecycle.delete()


class TestElasticSourceOfStockRepository:
    def test_add_to_source_of_stock_index(self):
        pass