import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elastic_repository import ElasticSpeciesRepository
from leaftracker.adapters.elasticsearch import DocumentStore, Lifecycle
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork, SPECIES_INDEX, SPECIES_MAPPINGS


@pytest.fixture
def uow() -> ElasticUnitOfWork:
    index_name = INDEX_TEST_PREFIX + SPECIES_INDEX
    store = DocumentStore(index_name)
    repository = ElasticSpeciesRepository(store)
    uow = ElasticUnitOfWork(repository)
    uow.commit()
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


def test_should_clear_queue_on_rollback(uow, saligna):
    with uow:
        uow.species().add(saligna)

    assert not uow.species().added()


def test_should_rollback_explicitly(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.rollback()
        assert not uow.species().added()


def test_should_clear_queue_after_commit(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()
        assert not uow.species().added()
