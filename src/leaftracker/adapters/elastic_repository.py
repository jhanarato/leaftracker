from dataclasses import dataclass
from typing import Any

from elastic_transport import ObjectApiResponse
from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species, ScientificName


@dataclass
class Document:
    document_id: str | None
    source: dict


class Index:
    def __init__(self, name: str, mappings: dict):
        self._client = Elasticsearch(hosts="http://localhost:9200")
        self._name = name
        self._mappings = mappings

    @property
    def name(self) -> str:
        return self._name

    def create(self):
        if self._client.indices.exists(index=self._name).body:
            return

        self._client.indices.create(index=self._name, mappings=self._mappings)

    def delete(self) -> None:
        self._client.options(ignore_status=404).indices.delete(index=self._name)

    def exists(self) -> bool:
        return self._client.indices.exists(index=self._name).body

    def refresh(self) -> None:
        self._client.indices.refresh(index=self._name)

    def document_count(self) -> int:
        return self._client.count(index=self._name)["count"]

    def delete_all_documents(self) -> None:
        self._client.delete_by_query(
            index=self._name,
            body={
                "query": {"match_all": {}}
            }
        )

    def document_exists(self, document_id: str) -> bool:
        return self._client.exists(index=self.name, id=document_id).body

    def add_document(self, document: dict, document_id: str | None) -> str:
        response = self._client.index(
            index=self.name,
            id=document_id,
            document=document
        )
        return response["_id"]

    def get_document(self, document_id) -> ObjectApiResponse[Any]:
        return self._client.get(index=self.name, id=document_id)


class SpeciesRepository:
    def __init__(self):
        mappings = {
            "properties": {
                "genus": {"type": "text"},
                "species": {"type": "text"},
            }
        }

        self.index = Index("species", mappings)
        self._queued: list[Document] = []

    def add(self, species: Species):
        document = Document(
            document_id=species.reference,
            source={
                "genus": species.names[0].genus,
                "species": species.names[0].species,
            }
        )

        self._queued.append(document)

        species.reference = self.index.add_document(document.source, document.document_id)

    def get(self, reference: str) -> Species:
        response = self.index.get_document(reference)
        return Species(
            reference=response["_id"],
            name=ScientificName(
                genus=response["_source"]["genus"],
                species=response["_source"]["species"]
            )
        )

    def queued(self) -> list[Document]:
        return self._queued

    def clear_queue(self) -> None:
        self._queued.clear()
