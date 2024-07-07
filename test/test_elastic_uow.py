import pytest

from conftest import INDEX_TEST_PREFIX
from leaftracker.adapters.elasticsearch import DocumentStore
from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork, SPECIES_INDEX


def test_should_normally_use_production_index():
    uow = ElasticUnitOfWork()
    assert uow.species().index == SPECIES_INDEX


def test_should_add_index_prefix():
    uow = ElasticUnitOfWork(INDEX_TEST_PREFIX)
    assert uow.species().index == INDEX_TEST_PREFIX + SPECIES_INDEX


@pytest.fixture
def uow() -> ElasticUnitOfWork:
    uow = ElasticUnitOfWork(INDEX_TEST_PREFIX)
    store = DocumentStore(INDEX_TEST_PREFIX + SPECIES_INDEX)
    store.delete_all()
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

    store = DocumentStore(INDEX_TEST_PREFIX + SPECIES_INDEX)
    assert store.count() == 2


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
