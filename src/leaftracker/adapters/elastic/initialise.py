from leaftracker.adapters.elastic.elasticsearch import Lifecycle, DocumentStore
from leaftracker.adapters.elastic.repositories.batch import BATCH_INDEX, BATCH_MAPPINGS, ElasticBatchRepository
from leaftracker.adapters.elastic.repositories.source_of_stock import SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS, \
    ElasticSourceOfStockRepository
from leaftracker.adapters.elastic.repositories.species import SPECIES_INDEX, SPECIES_MAPPINGS, ElasticSpeciesRepository
from leaftracker.adapters.elastic.unit_of_work import ElasticUnitOfWork


def indexes() -> None:
    Lifecycle(SPECIES_INDEX, SPECIES_MAPPINGS).create()
    Lifecycle(SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS).create()
    Lifecycle(BATCH_INDEX, BATCH_MAPPINGS).create()


def unit_of_work() -> ElasticUnitOfWork:
    return ElasticUnitOfWork(
        ElasticSourceOfStockRepository(DocumentStore(SOURCE_OF_STOCK_INDEX)),
        ElasticSpeciesRepository(DocumentStore(SPECIES_INDEX)),
        ElasticBatchRepository(DocumentStore(BATCH_INDEX)),
    )