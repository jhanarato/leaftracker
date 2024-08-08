from itertools import count
from typing import Iterator

from leaftracker.adapters.elastic.elasticsearch import Document


def references(prefix: str) -> Iterator[str]:
    for i in count(start=1):
        yield f"{prefix}-{i:04}"


class FakeDocumentStore:
    def __init__(self, index: str):
        self._index = index
        self._references = references(self._index)
        self._documents: dict[str, Document] = dict()

    def index(self) -> str:
        return self._index

    def add(self, document: Document) -> str:
        if document.document_id is None:
            document.document_id = next(self._references)
        self._documents[document.document_id] = document
        return document.document_id

    def get(self, document_id) -> Document | None:
        return self._documents.get(document_id)

    def ids(self) -> list[str]:
        return [document.document_id
                for document in self._documents.values()
                if document.document_id is not None]


