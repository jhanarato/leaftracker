import pytest

from leaftracker.adapters.elastic_repository import (
    ElasticSpeciesRepository,
    ElasticSourceOfStockRepository,
    ElasticBatchRepository,
)
from leaftracker.domain.model import Batch, BatchType, StockSize, Stock

from leaftracker.service_layer.elastic_uow import ElasticUnitOfWork


@pytest.fixture
def uow(source_store, batch_store, species_store) -> ElasticUnitOfWork:
    return ElasticUnitOfWork(
        ElasticSourceOfStockRepository(source_store),
        ElasticSpeciesRepository(species_store),
        ElasticBatchRepository(batch_store)
    )


def test_should_add_two_species(uow, saligna, dentifera):
    with uow:
        uow.species().add(saligna)
        uow.species().add(dentifera)
        uow.commit()

    assert saligna.reference is not None
    assert dentifera.reference is not None
    assert saligna.reference != dentifera.reference


@pytest.fixture
def batch():
    batch = Batch("source_of_stock-xxxx", BatchType.PICKUP)
    stock = Stock("species-xxxx", 20, StockSize.POT)
    batch.add(stock)
    return batch


class TestCommit:
    def test_commit_source_of_stock(self, uow, source_store, trillion_trees):
        with uow:
            uow.sources().add(trillion_trees)
            uow.commit()

        assert source_store.ids() == ["source_of_stock-0001"]

    def test_commit_species(self, uow, species_store, saligna):
        with uow:
            uow.species().add(saligna)
            uow.commit()

        assert species_store.ids() == ["species-0001"]

    def test_commit_batch(self, uow, batch_store, batch):
        with uow:
            uow.batches().add(batch)
            uow.commit()

        assert batch_store.ids() == ["batch-0001"]

    def test_commit_all(self, uow, source_store, species_store, batch_store,
                        saligna, trillion_trees, batch):
        with uow:
            uow.sources().add(trillion_trees)
            uow.species().add(saligna)
            uow.batches().add(batch)
            uow.commit()

        assert source_store.ids() == ["source_of_stock-0001"]
        assert species_store.ids() == ["species-0001"]
        assert batch_store.ids() == ["batch-0001"]


class TestRollback:
    def test_implicit_rollback(self, uow, source_store, species_store, batch_store,
                               saligna, trillion_trees, batch):
        with uow:
            uow.sources().add(trillion_trees)
            uow.species().add(saligna)
            uow.batches().add(batch)

        with uow:
            uow.commit()

        assert not source_store.ids()
        assert not species_store.ids()
        assert not batch_store.ids()

    def test_explicit_rollback(self, uow, source_store, species_store, batch_store,
                               saligna, trillion_trees, batch):
        with uow:
            uow.sources().add(trillion_trees)
            uow.species().add(saligna)
            uow.batches().add(batch)
            uow.rollback()
            uow.commit()

        assert not source_store.ids()
        assert not species_store.ids()
        assert not batch_store.ids()
