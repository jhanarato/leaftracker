from elasticsearch import NotFoundError

from leaftracker.adapters.elasticsearch import Document, Index
from leaftracker.domain.model import Species

SPECIES_INDEX = "species"

SPECIES_MAPPINGS = {
    "properties": {
        "scientific_names": {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }
    }
}


def document_to_species(document: Document) -> Species:
    names = document.source["scientific_names"]

    current_name = names[-1]
    previous_names = names[:-1]

    species = Species(
        current_name=f"{current_name["genus"]} {current_name["species"]}",
        reference=document.document_id
    )

    for previous_name in previous_names:
        species.taxon_history.add_previous_name(
            f"{previous_name["genus"]} {previous_name["species"]}"
        )

    return species


def species_to_document(species: Species) -> Document:
    scientific_names = [
        {"genus": name.genus, "species": name.species}
        for name in species.taxon_history
    ]

    return Document(
        document_id=species.reference,
        source={"scientific_names": scientific_names}
    )


class SpeciesRepository:
    def __init__(self, index_name: str = SPECIES_INDEX):
        self._added: list[Species] = []
        self.index = Index(index_name, SPECIES_MAPPINGS)

    def add(self, species: Species):
        self._added.append(species)

    def get(self, reference: str) -> Species | None:
        try:
            document = self.index.get_document(reference)
        except NotFoundError:
            return None

        return document_to_species(document)

    def added(self) -> list[Species]:
        return self._added

    def commit(self):
        for species in self.added():
            document = species_to_document(species)
            species.reference = self.index.add_document(document)

        self._added.clear()

    def rollback(self):
        self._added.clear()
