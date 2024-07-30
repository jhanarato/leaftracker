from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository
from leaftracker.adapters.elasticsearch import DocumentStore, Document, Lifecycle
from leaftracker.domain.model import Species, SourceOfStock, SourceType
from leaftracker.service_layer.elastic_uow import SPECIES_MAPPINGS, SPECIES_INDEX, SOURCE_OF_STOCK_INDEX, \
    SOURCE_OF_STOCK_MAPPINGS

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
        lifecycle = Lifecycle(INDEX_PREFIX + SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS)
        lifecycle.create()

        source = SourceOfStock("Trillion Trees", SourceType.NURSERY, "source-0001")

        store = DocumentStore(INDEX_PREFIX + SOURCE_OF_STOCK_INDEX)
        repository = ElasticSourceOfStockRepository(store)
        repository.add(source)
        repository.commit()

        document = store.get(source.reference)

        assert document == Document(
            document_id="source-0001",
            source={
                "current_name": "Trillion Trees",
                "source_type": "nursery",
            }
        )

        lifecycle.delete()
