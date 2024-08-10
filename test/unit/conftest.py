import pytest

from leaftracker.adapters.elastic.repositories.species import ElasticSpeciesRepository
from leaftracker.adapters.elastic.repository import (
    ElasticBatchRepository,
)
from leaftracker.adapters.elastic.repositories.source_of_stock import ElasticSourceOfStockRepository, \
    SOURCE_OF_STOCK_INDEX
from leaftracker.domain.model import Species, SourceOfStock, SourceType
from leaftracker.adapters.elastic.unit_of_work import (
    ElasticUnitOfWork, SPECIES_INDEX, BATCH_INDEX
)
from fakes import FakeDocumentStore


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
def uow(source_store, species_store, batch_store):
    return ElasticUnitOfWork(
        ElasticSourceOfStockRepository(source_store),
        ElasticSpeciesRepository(species_store),
        ElasticBatchRepository(batch_store)
    )
