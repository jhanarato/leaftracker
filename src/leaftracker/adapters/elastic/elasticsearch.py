from dataclasses import dataclass

from elasticsearch import Elasticsearch, NotFoundError

HOST = "http://localhost:9200"
YES_I_KNOW_YOU_SHOULDNT_DO_THIS_IN_PRODUCTION_APIKEY = "ZUJWOHNKTUJkWE16WFF6S0dtZVA6UmZkYmdvR3ZUa3VKRmZNS05LVmxSdw=="

class Lifecycle:
    def __init__(self, name: str, mappings: dict):
        self._client = Elasticsearch(hosts=HOST, api_key=YES_I_KNOW_YOU_SHOULDNT_DO_THIS_IN_PRODUCTION_APIKEY)
        self._name = name
        self._mappings = mappings

    def create(self) -> None:
        if self.exists():
            return

        self._client.indices.create(index=self._name, mappings=self._mappings)

    def delete(self) -> None:
        self._client.options(ignore_status=404).indices.delete(index=self._name)

    def exists(self) -> bool:
        return self._client.indices.exists(index=self._name).body


@dataclass
class Document:
    document_id: str | None
    source: dict


class DocumentStore:
    def __init__(self, index: str):
        self._client = Elasticsearch(hosts=HOST, api_key=YES_I_KNOW_YOU_SHOULDNT_DO_THIS_IN_PRODUCTION_APIKEY)
        self._index = index

    def index(self) -> str:
        return self._index

    def add(self, document: Document) -> str:
        response = self._client.index(
            index=self.index(),
            id=document.document_id,
            document=document.source
        )
        return response["_id"]

    def get(self, document_id) -> Document | None:
        try:
            response = self._client.get(index=self.index(), id=document_id)
        except NotFoundError:
            return None

        return Document(
            document_id=response["_id"],
            source=response["_source"],
        )

    def exists(self, document_id: str) -> bool:
        return self._client.exists(index=self.index(), id=document_id).body
