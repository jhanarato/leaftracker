from leaftracker.domain.model import SourceOfStock, SourceType, Batch, BatchType, Species, Stock, StockSize
from leaftracker.service_layer.unit_of_work import UnitOfWork


class ServiceError(RuntimeError):
    pass


class NotFoundError(Exception):
    pass


def add_source_of_stock(name: str, source_type: str, uow: UnitOfWork) -> str:
    source = SourceOfStock(name, SourceType(source_type))

    with uow:
        uow.sources().add(source)
        uow.commit()

    if source.reference is None:
        raise ServiceError("Source of stock was not assigned a reference.")

    return source.reference


def add_batch(source_reference: str, batch_type: str, uow: UnitOfWork) -> str:
    with uow:
        source = uow.sources().get(source_reference)

        if not source:
            raise NotFoundError(f"No source with reference {source_reference}")

        batch = Batch(source_reference=source_reference, batch_type=BatchType(batch_type))
        uow.batches().add(batch)
        uow.commit()

    if batch.reference is None:
        raise ServiceError("Batch was not assigned a reference.")

    return batch.reference


def add_stock(batch_reference: str, species_reference: str,
              quantity: int, stock_size: str, uow: UnitOfWork) -> None:
    with uow:
        species = uow.species().get(species_reference)

        if species is None:
            raise NotFoundError(f"No species with reference {species_reference}")

        batch = uow.batches().get(batch_reference)

        if batch is None:
            raise NotFoundError(f"No batch with reference {batch_reference}")

        stock = Stock(species_reference, quantity, StockSize(stock_size))
        batch.add(stock)
        uow.batches().add(batch)
        uow.commit()


def add_species(current_name: str, uow: UnitOfWork) -> str:
    species = Species(current_name)

    with uow:
        uow.species().add(species)
        uow.commit()

    if species.reference is None:
        raise ServiceError("Species was not assigned a reference.")

    return species.reference


def rename_species(reference: str, name: str, uow: UnitOfWork) -> None:
    with uow:
        species = uow.species().get(reference)

        if species is None:
            raise ServiceError(f"No species for reference {reference}.")

        species.taxon_history.new_current_name(name)
        uow.species().add(species)
        uow.commit()
