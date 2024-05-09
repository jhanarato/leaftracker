from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species, ScientificName


class Index:
    def __init__(self, name: str, mappings: dict):
        self._es = Elasticsearch(hosts="http://localhost:9200")
        self._name = name
        self._mappings = mappings

    @property
    def name(self) -> str:
        return self._name

    def create(self):
        if self._es.indices.exists(index=self._name).body:
            return

        self._es.indices.create(index=self._name, mappings=self._mappings)

    def delete(self) -> None:
        self._es.options(ignore_status=404).indices.delete(index=self._name)

    def exists(self) -> bool:
        return self._es.indices.exists(index=self._name).body

    def refresh(self) -> None:
        self._es.indices.refresh(index=self._name)

    def count(self) -> int:
        return self._es.count(index=self._name)["count"]

    def delete_all_documents(self) -> None:
        self._es.delete_by_query(
            index=self._name,
            body={
                "query": {"match_all": {}}
            }
        )


class SpeciesRepository:
    def __init__(self):
        self._es = Elasticsearch(hosts="http://localhost:9200")
        self._index_name = "species"

        mappings = {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }

        self._index = Index("species", mappings)

    def add(self, species: Species) -> str:
        reference = species.reference
        document = {
            "genus": species.names[0].genus,
            "species": species.names[0].species,
        }

        response = self.index_document(document, reference)

        reference = response["_id"]
        species.reference = reference
        return reference

    def index_document(self, document: dict, reference: str):
        return self._es.index(
            index=self._index.name,
            id=reference,
            document=document
        )

    def get(self, species_ref: str) -> Species:
        doc = self._es.get(index=self._index.name, id=species_ref)
        reference = doc["_id"]
        name = ScientificName(
            genus=doc["_source"]["genus"],
            species=doc["_source"]["species"]
        )

        return Species(name, reference)
