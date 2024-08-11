import pytest

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, TaxonName


@pytest.fixture
def aggregate() -> Species:
    species = Species(current_name="Machaerina juncea", reference="species-0001")
    species.taxon_history.add_previous_name("Baumea juncea")
    return species


@pytest.fixture
def document() -> Document:
    return Document(
        document_id="species-0001",
        source={
            "current_scientific_name": "Machaerina juncea",
            "previous_scientific_names": ["Baumea juncea"]
        }
    )


class TestElasticSourceOfStockRepository:
    def test_add(self, uow, species_store, aggregate, document):
        with uow:
            uow.species().add(aggregate)
            uow.commit()

        stored = species_store.get(document.document_id)
        assert stored == document

    def test_get(self, uow, species_store, document):
        species_store.add(document)

        with uow:
            species = uow.species().get(document.document_id)

        assert species.reference == "species-0001"
        assert species.taxon_history.current() == TaxonName("Machaerina juncea")
        assert next(species.taxon_history.previous()) == TaxonName("Baumea juncea")
