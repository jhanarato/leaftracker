from collections.abc import Generator

import pytest
from elasticsearch import Elasticsearch

from leaftracker.adapters.elastic_repository import SpeciesRepository
from leaftracker.domain.model import Species, ScientificName


@pytest.fixture
def acacia() -> ScientificName:
    return ScientificName(
        genus="Acacia",
        species="Saligna",
        is_most_recent=True
    )


@pytest.fixture
def es() -> Elasticsearch:
    return Elasticsearch(hosts="http://localhost:9200")


@pytest.fixture
def new_repo() -> SpeciesRepository:
    repo = SpeciesRepository()
    repo.delete_index()
    repo.create_index()
    return repo


class TestSpeciesRepository:
    def test_should_create_new_index(self, es):
        es.options(ignore_status=404).indices.delete(index="species")
        repo = SpeciesRepository()
        repo.create_index()
        assert es.indices.exists(index="species")

    def test_should_delete_missing_index(self, es):
        repo = SpeciesRepository()
        repo.delete_index()
        repo.delete_index()
        assert not es.indices.exists(index="species")

    def test_should_delete_existing_index(self, es):
        repo = SpeciesRepository()
        repo.create_index()
        repo.delete_index()
        assert not es.indices.exists(index="species")

    def test_should_add_a_species(self, new_repo, acacia, es):
        reference = new_repo.add(Species("acacia-saligna", acacia))
        assert es.exists(index="species", id=reference)

    def test_should_get_a_species(self, new_repo, acacia):
        species_in = Species("acacia-saligna", acacia)
        new_repo.add(species_in)
        species_out = new_repo.get(species_in.reference)
        assert species_in == species_out

    def test_should_generate_reference_if_none_provided(self, new_repo, acacia, es):
        species = Species(None, acacia)
        reference = new_repo.add(species)
        assert reference is not None
