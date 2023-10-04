from datetime import date

from revegetator.adapters.repository import BatchRepository
from revegetator.domain.model import Batch, Stock


class FakeBatchRepository:
    def __init__(self, batches: list[Batch]):
        self._batches = set(batches)

    def _new_reference(self) -> str:
        return "batch-01"

    def add(self, batch: Batch) -> str:
        batch.reference = self._new_reference()
        self._batches.add(batch)
        return batch.reference

    def get(self, batch_ref: str) -> Batch | None:
        matching = (batch for batch in self._batches
                    if batch.reference == batch_ref)
        return next(matching, None)


def test_should_catalogue_batch():
    repo: BatchRepository = FakeBatchRepository([])

    batch_ref = "batch-01"

    batch_to_repo = Batch(
        reference=None,
        # TODO: Origin should be an entity
        origin="Trillion Trees",
        # TODO: date should be on an order or delivery.
        date_received=date(2020, 5, 15)
    )

    batch_to_repo.add(Stock(species_ref="Acacia saligna", quantity=20, size="tube"))

    repo.add(batch_to_repo)

    batch_from_repo = repo.get(batch_ref)

    assert batch_from_repo.reference == batch_ref
