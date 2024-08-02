import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository, \
    ElasticBatchRepository
from leaftracker.domain.model import Species, SourceOfStock, SourceType
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


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
def fake_uow():
    sources_store = FakeDocumentStore("source_of_stock")
    sources_repository = ElasticSourceOfStockRepository(sources_store)

    species_store = FakeDocumentStore("species")
    species_repository = ElasticSpeciesRepository(species_store)

    batches_store = FakeDocumentStore("batches")
    batches_repository = ElasticBatchRepository(batches_store)

    return ElasticUnitOfWork(sources_repository, species_repository, batches_repository)
