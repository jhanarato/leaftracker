from revegetator.adapters.repository import BatchRepository
from revegetator.domain.model import Batch, Stock, Source, StockSize, BatchType, SourceType


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


def test_fake_reference():
    repo: BatchRepository = FakeBatchRepository([])

    source_a = Source("Habitat Links", SourceType.PROGRAM)
    source_b = Source("Natural Area", SourceType.NURSERY)

    references = [repo.add(Batch(source_a, BatchType.DELIVERY)),
                  repo.add(Batch(source_a, BatchType.DELIVERY)),
                  repo.add(Batch(source_b, BatchType.DELIVERY))]

    assert references == ["batch-0001", "batch-0002", "batch-0003"]


def test_should_catalogue_batch():
    repo: BatchRepository = FakeBatchRepository([])

    batch_to_repo = Batch(
        source=Source("Trillion Trees", SourceType.NURSERY), batch_type=BatchType.PICKUP)

    batch_to_repo.add(Stock(species_ref="Acacia saligna", quantity=20, size=StockSize.TUBE))

    ref = repo.add(batch_to_repo)

    batch_from_repo = repo.get(ref)

    assert batch_from_repo.source.name == "Trillion Trees"
    assert batch_from_repo.source.source_type == SourceType.NURSERY
    assert batch_from_repo.species() == ["Acacia saligna"]
