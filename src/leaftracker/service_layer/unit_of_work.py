from typing import Protocol, Self

from leaftracker.adapters.repository import BatchRepository, SourceOfStockRepository, SpeciesRepository


class UnitOfWork(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(self, *args): ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...

    def batches(self) -> BatchRepository: ...

    def sources(self) -> SourceOfStockRepository: ...

    def species(self) -> SpeciesRepository: ...
