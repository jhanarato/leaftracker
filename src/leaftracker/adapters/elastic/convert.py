from leaftracker.adapters.elastic.elasticsearch import Document
from leaftracker.domain.model import Species, SourceOfStock, SourceType, Batch, BatchType, Stock


def document_to_species(document: Document) -> Species:
    current_name = document.source["current_scientific_name"]
    previous_names = document.source["previous_scientific_names"]

    species = Species(
        current_name=current_name,
        reference=document.document_id
    )

    for previous_name in previous_names:
        species.taxon_history.add_previous_name(previous_name)

    return species


def species_to_document(species: Species) -> Document:
    current_scientific_name = str(species.taxon_history.current())
    other_scientific_names = [str(name) for name in species.taxon_history.previous()]

    return Document(
        document_id=species.reference,
        source={
            "current_scientific_name": current_scientific_name,
            "previous_scientific_names": other_scientific_names,
        }
    )


def source_to_document(source: SourceOfStock) -> Document:
    current_name = source.current_name
    source_type = source.source_type.value

    return Document(
        document_id=source.reference,
        source={
            "current_name": current_name,
            "source_type": source_type,
        }
    )


def document_to_source(document: Document) -> SourceOfStock:
    reference = document.document_id
    current_name = document.source["current_name"]
    source_type = document.source["source_type"]

    return SourceOfStock(current_name, SourceType(source_type), reference)


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
