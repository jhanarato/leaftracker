from dataclasses import dataclass

from elasticsearch import Elasticsearch

HOSTS = "http://localhost:9200"


class Lifecycle:
    def __init__(self, name: str, mappings: dict):
        self._client = Elasticsearch(hosts=HOSTS)
        self._name = name
        self._mappings = mappings

    def create(self):
        if self.exists():
            return

        self._client.indices.create(index=self._name, mappings=self._mappings)

    def delete(self) -> None:
        self._client.options(ignore_status=404).indices.delete(index=self._name)

    def exists(self) -> bool:
        return self._client.indices.exists(index=self._name).body

    def refresh(self) -> None:
        self._client.indices.refresh(index=self._name)


@dataclass
class Document:
    document_id: str | None
    source: dict


class DocumentStore:
    def __init__(self, name: str):
        self._client = Elasticsearch(hosts=HOSTS)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def count(self) -> int:
        return self._client.count(index=self._name)["count"]

    def delete_all(self) -> None:
        self._client.delete_by_query(
            index=self._name,
            body={"query": {"match_all": {}}}
        )

    def exists(self, document_id: str) -> bool:
        return self._client.exists(index=self.name, id=document_id).body

    def add(self, document: Document) -> str:
        response = self._client.index(
            index=self.name,
            id=document.document_id,
            document=document.source
        )
        return response["_id"]

    def get(self, document_id) -> Document:
        response = self._client.get(index=self.name, id=document_id)
        return Document(
            document_id=response["_id"],
            source=response["_source"],
        )
