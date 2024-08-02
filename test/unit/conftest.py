import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository, \
    ElasticBatchRepository
from leaftracker.domain.model import Species, SourceOfStock, SourceType
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork, SOURCE_OF_STOCK_INDEX, SPECIES_INDEX, BATCH_INDEX
from unit.fakes import FakeDocumentStore


@pytest.fixture
def saligna() -> Species:
    species = Species("Acacia saligna")
    return species


@pytest.fixture
def dentifera() -> Species:
    species = Species("Acacia dentifera")
    return species


@pytest.fixture
def trillion_trees() -> SourceOfStock:
    return SourceOfStock("Trillion Trees", SourceType.NURSERY)


@pytest.fixture
def source_store() -> FakeDocumentStore:
    return FakeDocumentStore(SOURCE_OF_STOCK_INDEX)


@pytest.fixture
def species_store() -> FakeDocumentStore:
    return FakeDocumentStore(SPECIES_INDEX)


@pytest.fixture
def batch_store() -> FakeDocumentStore:
    return FakeDocumentStore(BATCH_INDEX)


@pytest.fixture
def fake_uow(source_store, species_store, batch_store):
    sources_repository = ElasticSourceOfStockRepository(source_store)
    species_repository = ElasticSpeciesRepository(species_store)
    batches_repository = ElasticBatchRepository(batch_store)

    return ElasticUnitOfWork(sources_repository, species_repository, batches_repository)
