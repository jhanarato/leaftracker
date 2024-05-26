import pytest
from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species, ScientificName


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
