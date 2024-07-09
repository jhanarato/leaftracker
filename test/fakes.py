from itertools import count
from typing import Iterator

from leaftracker.adapters.elasticsearch import Document


def references(prefix: str) -> Iterator[str]:
    for i in count(start=1):
        yield f"{prefix}-{i:04}"


class FakeLifecycle:
    def __init__(self, exists: bool):
        self._exists = exists

    def create(self) -> None:
        self._exists = True

    def delete(self) -> None:
        self._exists = False

    def exists(self) -> bool:
        return self._exists

    def refresh(self) -> None:
        pass


class FakeDocumentStore:
    def __init__(self, index: str):
        self._index = index
        self._references = references(self._index)
        self._store: dict[str, Document] = dict()

    def index(self) -> str:
        return self._index

    def add(self, document: Document) -> str:
        if document.document_id is None:
            document.document_id = next(self._references)
        self._store[document.document_id] = document
        return document.document_id

    def get(self, document_id) -> Document:
        return self._store[document_id]
