from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species, ScientificName


class SpeciesRepository:
    def __init__(self):
        self._es = Elasticsearch(hosts="http://localhost:9200")
        self._index = "species"

    @property
    def index(self) -> str:
        return self._index

    def create_index(self):
        if self._es.indices.exists(index=self._index):
            return

        mappings = {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }
        self._es.indices.create(index=self.index, mappings=mappings)

    def refresh(self) -> None:
        self._es.indices.refresh(index=self.index)

    def count(self) -> int:
        return self._es.count(index=self.index)["count"]

    def delete_index(self) -> None:
        self._es.options(ignore_status=404).indices.delete(index=self.index)

    def delete_all_documents(self) -> None:
        self._es.delete_by_query(
            index=self.index,
            body={
                "query": {"match_all": {}}
            }
        )

    def add(self, species: Species) -> str:
        response = self._es.index(
            index=self.index,
            id=species.reference,
            document={
                "genus": species.names[0].genus,
                "species": species.names[0].species,
            }
        )
        return response["_id"]

    def get(self, species_ref: str) -> Species:
        doc = self._es.get(index=self.index, id=species_ref)
        reference = doc["_id"]
        name = ScientificName(
            genus=doc["_source"]["genus"],
            species=doc["_source"]["species"]
        )

        return Species(name, reference)
