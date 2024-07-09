from typing import Self

import pytest
from elasticsearch import Elasticsearch

from fakes import references
from leaftracker.adapters.repository import BatchRepository, SourceRepository, SpeciesRepository
from leaftracker.domain.model import Species, Batch, Source

INDEX_TEST_PREFIX = "test_"


@pytest.fixture
def saligna() -> Species:
    species = Species("Acacia saligna")
    return species


@pytest.fixture
def dentifera() -> Species:
    species = Species("Acacia dentifera")
    return species


def delete_test_indexes():
    client = Elasticsearch(hosts="http://localhost:9200")
    aliases = client.indices.get_alias(index="test_*")
    for alias in aliases:
        client.options(ignore_status=404).indices.delete(index=alias)


@pytest.fixture(autouse=True, scope='session')
def test_indexes():
    yield
    delete_test_indexes()


class FakeSpeciesRepository:
    def __init__(self):
        self._added = set()
        self._committed = dict()
        self.references = references("species")

    def add(self, species: Species):
        self._added.add(species)

    def get(self, reference: str) -> Species | None:
        return self._committed.get(reference)

    def commit(self):
        for species in self._added:
            species.reference = next(self.references)
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

    def set_species(self, repository: FakeSpeciesRepository):
        self._species = repository
