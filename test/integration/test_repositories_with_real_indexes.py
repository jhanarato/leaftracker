from leaftracker.adapters.elastic.repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository, \
    ElasticBatchRepository
from leaftracker.adapters.elastic.elasticsearch import DocumentStore, Document, Lifecycle
from leaftracker.domain.model import Species, SourceOfStock, SourceType, Batch, BatchType, Stock, StockSize
from leaftracker.adapters.elastic.unit_of_work import SPECIES_MAPPINGS, SPECIES_INDEX, SOURCE_OF_STOCK_INDEX, \
    SOURCE_OF_STOCK_MAPPINGS, BATCH_INDEX, BATCH_MAPPINGS

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
        repository.writer.write()

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
        repository.writer.write()

        document = store.get(source.reference)

        assert document == Document(
            document_id="source-0001",
            source={
                "current_name": "Trillion Trees",
                "source_type": "nursery",
            }
        )

        lifecycle.delete()


class TestElasticBatchRepository:
    def test_add_to_batch_index(self):
        lifecycle = Lifecycle(INDEX_PREFIX + BATCH_INDEX, BATCH_MAPPINGS)
        lifecycle.create()

        batch = Batch("source-0001", BatchType.PICKUP, "batch-0001")
        batch.add(Stock("species-0001", 20, StockSize.TUBE))
        batch.add(Stock("species-0002", 5, StockSize.POT))

        store = DocumentStore(INDEX_PREFIX + BATCH_INDEX)
        repository = ElasticBatchRepository(store)
        repository.add(batch)
        repository.writer.write()

        document = store.get(batch.reference)

        assert document == Document(
            document_id="batch-0001",
            source={
                "source_reference": "source-0001",
                "batch_type": "pickup",
                "stock": [
                    {
                        "species_reference": "species-0001",
                        "quantity": 20,
                        "size": "tube",
                    },
                    {
                        "species_reference": "species-0002",
                        "quantity": 5,
                        "size": "pot",
                    },
                ]
            }
        )

        lifecycle.delete()
