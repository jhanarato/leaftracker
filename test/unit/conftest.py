import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic.repositories.batch import ElasticBatchRepository, BATCH_INDEX
from leaftracker.adapters.elastic.repositories.source_of_stock import (
    ElasticSourceOfStockRepository, SOURCE_OF_STOCK_INDEX
)
from leaftracker.adapters.elastic.repositories.species import ElasticSpeciesRepository, SPECIES_INDEX
from leaftracker.adapters.elastic.unit_of_work import ElasticUnitOfWork
from leaftracker.domain.model import Species, SourceOfStock, SourceType


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
