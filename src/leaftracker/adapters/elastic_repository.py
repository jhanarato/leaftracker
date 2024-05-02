from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species, ScientificName


class SpeciesRepository:
    def __init__(self):
        self._es = Elasticsearch(hosts="http://localhost:9200")

    def create_index(self):
        mappings = {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }
        self._es.indices.create(index="species", mappings=mappings)

    def delete_index(self):
        self._es.options(ignore_status=404).indices.delete(index="species")

    def add(self, species: Species) -> str:
        response = self._es.index(
            index="species",
            id=species.reference,
            document={
                "genus": species.names[0].genus,
                "species": species.names[0].species,
            }
        )
        return response["_id"]

    def get(self, species_ref: str) -> Species:
        doc = self._es.get(index="species", id=species_ref)
        ref = doc["_id"]
        name = ScientificName(
            genus=doc["_source"]["genus"],
            species=doc["_source"]["species"]
        )

        return Species(ref, name)
