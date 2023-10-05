from typing import Self

import pytest

from revegetator.adapters.repository import BatchRepository, SourceRepository
from revegetator.domain.model import Batch, Source, SourceType, BatchType, Stock, StockSize
from revegetator.service_layer import services
from revegetator.service_layer.services import InvalidSource
from revegetator.service_layer.unit_of_work import UnitOfWork


class FakeBatchRepository:
    def __init__(self, batches: list[Batch]):
        self._batches = set(batches)

    def _new_reference(self) -> str:
        highest = max([int(batch.reference[-2:]) for batch in self._batches], default=0)
        new_number = highest + 1
        return f"batch-{new_number:04}"

    def add(self, batch: Batch) -> str:
        batch.reference = self._new_reference()
        self._batches.add(batch)
        return batch.reference

    def get(self, batch_ref: str) -> Batch | None:
        matching = (batch for batch in self._batches
                    if batch.reference == batch_ref)
        return next(matching, None)


class FakeSourceRepository:
    def __init__(self, sources: list[Source]):
        self._sources = set(sources)

    def add(self, source: Source) -> str:
        self._sources.add(source)
        return source.name

    def get(self, name: str) -> Source | None:
        matching = (source for source in self._sources
                    if source.name == name)
        return next(matching, None)


def test_fake_reference():
    repo: BatchRepository = FakeBatchRepository([])

    references = [repo.add(Batch("Habitat Links", BatchType.DELIVERY)),
                  repo.add(Batch("Habitat Links", BatchType.DELIVERY)),
                  repo.add(Batch("Natural Area", BatchType.DELIVERY))]

    assert references == ["batch-0001", "batch-0002", "batch-0003"]


class FakeUnitOfWork:
    def __init__(self):
        self._batches: BatchRepository = FakeBatchRepository([])
        self._sources: SourceRepository = FakeSourceRepository([])
        self._commited = False

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._commited = True

    def committed(self) -> bool:
        return self._commited

    def rollback(self) -> None:
        pass

    def batches(self) -> BatchRepository:
        return self._batches

    def sources(self) -> SourceRepository:
        return self._sources


def test_should_catalogue_batch():
    uow: UnitOfWork = FakeUnitOfWork()

    with uow:
        batch = Batch(
            source_name="Trillion Trees",
            batch_type=BatchType.PICKUP
        )

        batch.add(Stock(species_ref="Acacia saligna", quantity=20, size=StockSize.TUBE))

        ref = uow.batches().add(batch)
        uow.commit()

        new_batch = uow.batches().get(ref)

    assert new_batch.source_name == "Trillion Trees"
    assert new_batch.species() == ["Acacia saligna"]


def test_add_nursery():
    uow: UnitOfWork = FakeUnitOfWork()

    services.add_nursery("Trillion Trees", uow)

    assert uow.sources().get("Trillion Trees").source_type == SourceType.NURSERY
    assert uow.committed()


def test_add_program():
    uow: UnitOfWork = FakeUnitOfWork()

    services.add_program("Habitat Links", uow)

    assert uow.sources().get("Habitat Links").source_type == SourceType.PROGRAM
    assert uow.committed()


def test_add_order():
    uow: UnitOfWork = FakeUnitOfWork()

    program = "Habitat Links"
    services.add_program(program, uow)
    ref = services.add_order(program, uow)

    assert ref == "batch-0001"

    assert uow.batches().get(ref).batch_type == BatchType.ORDER
    assert uow.committed()


def test_missing_source():
    uow: UnitOfWork = FakeUnitOfWork()

    with pytest.raises(InvalidSource, match="No such source of stock"):
        services.add_order("Missing", uow)
