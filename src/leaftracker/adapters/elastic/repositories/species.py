from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.adapters.elastic.repository import DocumentStore, AggregateWriter, AggregateReader
from leaftracker.domain.model import Species

SPECIES_INDEX = "species"
SPECIES_MAPPINGS = {
    "properties": {
        "current_scientific_name": {"type": "text"},
        "previous_scientific_names": {"type": "text"},
    }
}


def document_to_species(document: Document) -> Species:
    current_name = document.source["current_scientific_name"]
    previous_names = document.source["previous_scientific_names"]

    species = Species(
        current_name=current_name,
        reference=document.document_id
    )

    for previous_name in previous_names:
        species.taxon_history.add_previous_name(previous_name)

    return species


def species_to_document(species: Species) -> Document:
    current_scientific_name = str(species.taxon_history.current())
    other_scientific_names = [str(name) for name in species.taxon_history.previous()]

    return Document(
        document_id=species.reference,
        source={
            "current_scientific_name": current_scientific_name,
            "previous_scientific_names": other_scientific_names,
        }
    )


class ElasticSpeciesRepository:
    def __init__(self, store: DocumentStore):
        self.writer = AggregateWriter[Species](store, species_to_document)
        self.reader = AggregateReader[Species](store, document_to_species)

    def add(self, species: Species):
        self.writer.add(species)

    def get(self, reference: str) -> Species | None:
        return self.reader.read(reference)
