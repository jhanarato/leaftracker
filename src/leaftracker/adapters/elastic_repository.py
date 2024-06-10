from elasticsearch import NotFoundError

from leaftracker.adapters.elastic_index import Document, Index
from leaftracker.domain.model import Species, TaxonName

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
    first_taxon_name = TaxonName(names[0]["genus"], names[0]["species"])
    species = Species(first_taxon_name)
    species.taxon_history.new_name(str(first_taxon_name))

    for name in names[1:]:
        next_taxon_name = TaxonName(name["genus"], name["species"])
        species.taxon_history.new_name(str(next_taxon_name))

    return species


def species_to_document(species: Species) -> Document:
    scientific_names = [
        {"genus": name.genus, "species": name.species}
        for name in species.taxon_history.oldest_to_newest()
    ]

    return Document(
        document_id=species.reference,
        source={"scientific_names": scientific_names}
    )


class SpeciesRepository:
    def __init__(self, index_name: str = SPECIES_INDEX):
        self.index = Index(index_name, SPECIES_MAPPINGS)
        self.index.create()

        self._added: list[Species] = []

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

        self.index.refresh()
        self._added.clear()

    def rollback(self):
        self._added.clear()
