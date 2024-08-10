from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, Batch, BatchType, Stock


def stock_for_document(batch: Batch) -> list[dict]:
    return [
        {
            "species_reference": stock.species_reference,
            "quantity": stock.quantity,
            "size": stock.size.value,
        }
        for stock in batch.stock
    ]


def batch_to_document(batch: Batch) -> Document:
    source_reference = batch.source_reference
    batch_type = batch.batch_type.value
    stock = stock_for_document(batch)

    return Document(
        document_id=batch.reference,
        source={
            "source_reference": source_reference,
            "batch_type": batch_type,
            "stock": stock
        }
    )


def document_to_batch(document: Document) -> Batch:
    source_reference = document.source["source_reference"]
    batch_type = document.source["batch_type"]
    batch_reference = document.document_id

    batch = Batch(source_reference, BatchType(batch_type), batch_reference)

    for stock in document.source["stock"]:
        species_reference = stock["species_reference"]
        quantity = stock["quantity"]
        size = stock["size"]

        batch.add(Stock(species_reference, quantity, size))

    return batch
