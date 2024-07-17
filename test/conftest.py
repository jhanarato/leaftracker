import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.domain.model import Species
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork

INDEX_TEST_PREFIX = "test_"


@pytest.fixture
def saligna() -> Species:
    species = Species("Acacia saligna")
    return species


@pytest.fixture
def dentifera() -> Species:
    species = Species("Acacia dentifera")
    return species


@pytest.fixture
def fake_uow():
    store = FakeDocumentStore("species")
    repository = ElasticSpeciesRepository(store)
    return ElasticUnitOfWork(repository)
