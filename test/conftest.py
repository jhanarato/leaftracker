from typing import Self

import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.repository import BatchRepository, SourceRepository, SpeciesRepository
from leaftracker.domain.model import Species, ScientificName, Batch, Source


@pytest.fixture
def saligna() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )
    )


@pytest.fixture
def dentifera() -> Species:
    return Species(
        ScientificName(
            genus="Acacia",
            species="Dentifera",
            is_most_recent=True
        )
    )


@pytest.fixture(autouse=True, scope='session')
def delete_test_indexes():
    yield
    es = Elasticsearch(hosts="http://localhost:9200")
    es.indices.delete(index=["test_index", "test_species"])


class FakeBatchRepository:
    def __init__(self, batches: list[Batch]):
        self._next_batch_number = 1
        self._batches = set(batches)

    def _new_reference(self) -> str:
        reference = f"batch-{self._next_batch_number:04}"
        self._next_batch_number += 1
        return reference

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


class FakeSpeciesRepository:
    def __init__(self, species: list[Species]):
        self._species = set(species)

    def add(self, species: Species) -> str | None:
        self._species.add(species)
        return species.reference

    def get(self, reference: str) -> Species | None:
        matching = (species for species in self._species
                    if species.reference == reference)
        return next(matching, None)


class FakeUnitOfWork:
    def __init__(self):
        self._batches: BatchRepository = FakeBatchRepository([])
        self._sources: SourceRepository = FakeSourceRepository([])
        self._species: SpeciesRepository = FakeSpeciesRepository([])
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

    def species(self) -> SpeciesRepository:
        return self._species
