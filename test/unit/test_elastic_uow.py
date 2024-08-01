import pytest

from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository, ElasticSourceOfStockRepository, \
    ElasticBatchRepository
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork
from fakes import FakeDocumentStore


@pytest.fixture
def species_store() -> FakeDocumentStore:
    return FakeDocumentStore("species")


@pytest.fixture
def species_repository(species_store) -> ElasticSpeciesRepository:
    return ElasticSpeciesRepository(species_store)


@pytest.fixture
def uow(species_repository) -> ElasticUnitOfWork:
    sources_store = FakeDocumentStore("source_of_stock")
    sources_repository = ElasticSourceOfStockRepository(sources_store)

    batches_store = FakeDocumentStore("batches")
    batches_repository = ElasticBatchRepository(batches_store)

    uow = ElasticUnitOfWork(sources_repository, species_repository, batches_repository)
    return uow


def test_should_rollback_if_not_committed(uow, saligna):
    with uow:
        uow.species().add(saligna)

    assert saligna.reference is None


def test_should_commit(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()

    assert saligna.reference is not None


def test_should_add_two_species(uow, saligna, dentifera):
    with uow:
        uow.species().add(saligna)
        uow.species().add(dentifera)
        uow.commit()

    assert saligna.reference is not None
    assert dentifera.reference is not None
    assert saligna.reference != dentifera.reference


def test_should_clear_queue_on_rollback(uow, species_repository, saligna):
    with uow:
        uow.species().add(saligna)

    assert not species_repository.added()


def test_should_rollback_explicitly(uow, species_repository, saligna):
    with uow:
        uow.species().add(saligna)
        uow.rollback()

    assert not species_repository.added()


def test_should_clear_queue_after_commit(uow, species_repository, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()

    assert not species_repository.added()
