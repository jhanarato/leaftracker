import pytest

from fakes import FakeDocumentStore
from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.adapters.elastic.aggregate_io import AggregateWriter, AggregateReader


class Aggregate:
    def __init__(self, number: int, reference: str | None = None):
        self.reference = reference
        self.number = number


def to_document(aggregate: Aggregate) -> Document:
    return Document(aggregate.reference, {"number": aggregate.number})


REFERENCE = "aggregate-xxxx"


@pytest.fixture
def aggregate() -> Aggregate:
    return Aggregate(123, REFERENCE)


@pytest.fixture
def document() -> Document:
    return Document(REFERENCE, {"number": 123})


@pytest.fixture
def store() -> FakeDocumentStore:
    return FakeDocumentStore("aggregate")


@pytest.fixture
def writer(store) -> AggregateWriter:
    return AggregateWriter[Aggregate](store, to_document)


class TestAggregateWriter:
    def test_add_pending_change(self, writer, aggregate):
        writer.add(aggregate)
        assert list(writer.added()) == [aggregate]

    def test_discards_added_after_write(self, writer, aggregate):
        writer.add(aggregate)
        writer.write()
        assert list(writer.added()) == []

    def test_writes_to_document(self, writer, store, aggregate, document):
        writer.add(aggregate)
        writer.write()

        assert store.get(REFERENCE) == document

    def test_assigns_reference_when_missing(self, writer, aggregate, store):
        aggregate.reference = None
        writer.add(aggregate)
        writer.write()
        assert aggregate.reference == "aggregate-0001"


def to_aggregate(document: Document) -> Aggregate:
    aggregate = Aggregate(
        reference=document.document_id,
        number=document.source["number"]
    )
    return aggregate


@pytest.fixture
def reader(store) -> AggregateReader:
    return AggregateReader[Aggregate](store, to_aggregate)


class TestAggregateReader:
    def test_read_existing_document(self, reader, store, document):
        store.add(document)
        aggregate = reader.read(document.document_id)
        assert aggregate is not None
        assert aggregate.reference == document.document_id
        assert aggregate.number == 123

    def test_read_missing_document(self, reader):
        assert reader.read("aggregate-xxxx") is None
