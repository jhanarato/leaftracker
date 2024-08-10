import pytest

from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species


@pytest.fixture
def species_aggregate() -> Species:
    species = Species(current_name="Machaerina juncea", reference="species-0001")
    species.taxon_history.add_previous_name("Baumea juncea")
    return species


@pytest.fixture
def species_document() -> Document:
    return Document(
        document_id="species-0001",
        source={
            "current_scientific_name": "Machaerina juncea",
            "previous_scientific_names": ["Baumea juncea"]
        }
    )
