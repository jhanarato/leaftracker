import pytest

from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


def test_should_normally_use_production_index():
    uow = ElasticUnitOfWork()
    assert uow.species().index.name == "species"


def test_should_use_test_index_if_specified():
    uow = ElasticUnitOfWork(use_test_indexes=True)
    assert uow.species().index.name == "test_species"


@pytest.fixture
def uow() -> ElasticUnitOfWork:
    uow = ElasticUnitOfWork(use_test_indexes=True)
    uow.species().index.delete_all_documents()
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

    assert uow.species().index.document_count() == 2


def test_should_clear_queue_on_rollback(uow, saligna):
    with uow:
        uow.species().add(saligna)

    assert not uow.species().queued()


def test_should_rollback_explicitly(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.rollback()
        assert not uow.species().queued()


def test_should_clear_queue_after_commit(uow, saligna):
    with uow:
        uow.species().add(saligna)
        uow.commit()
        assert not uow.species().queued()


def test_should_get_all_indexes(uow):
    index_names = [index.name for index in uow.indexes()]
    assert index_names == ["test_species"]
