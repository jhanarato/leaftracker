from itertools import count
from typing import Self, Iterator

import pytest

from leaftracker.adapters.repository import BatchRepository, SourceRepository, SpeciesRepository
from leaftracker.domain.model import Species, TaxonName, Batch, Source, TaxonHistory
from tools import delete_test_indexes

INDEX_TEST_PREFIX = "test_"


@pytest.fixture
def saligna() -> Species:
    taxons = TaxonHistory()
    taxons.new_name("Acacia saligna")
    return Species(
        TaxonName(
            genus="Acacia",
            species="saligna",
            is_most_recent=True
        ),
        taxons
    )


@pytest.fixture
def dentifera() -> Species:
    taxons = TaxonHistory()
    return Species(
        TaxonName(
            genus="Acacia",
            species="dentifera",
            is_most_recent=True
        ),
        taxons
    )


@pytest.fixture(autouse=True, scope='session')
def test_indexes():
    yield
    delete_test_indexes()


def references(prefix: str) -> Iterator[str]:
    for i in count(start=1):
        yield f"{prefix}-{i:04}"


class FakeSpeciesRepository:
    def __init__(self):
        self._added = set()
        self._committed = dict()
        self._references = references("species")

    def add(self, species: Species):
        self._added.add(species)

    def get(self, reference: str) -> Species | None:
        return self._committed.get(reference)

    def commit(self):
        for species in self._added:
            species.reference = next(self._references)
            self._committed[species.reference] = species

    def rollback(self):
        self._added.clear()


class FakeBatchRepository:
    def __init__(self, batches: list[Batch]):
        self._references = references("batch")
        self._batches = set(batches)

    def add(self, batch: Batch) -> str:
        batch.reference = next(self._references)
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


class FakeUnitOfWork:
    def __init__(self):
        self._batches = FakeBatchRepository([])
        self._sources = FakeSourceRepository([])
        self._species = FakeSpeciesRepository()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self) -> None:
        self._species.commit()

    def rollback(self) -> None:
        self._species.rollback()

    def batches(self) -> BatchRepository:
        return self._batches

    def sources(self) -> SourceRepository:
        return self._sources

    def species(self) -> SpeciesRepository:
        return self._species
