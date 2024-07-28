from leaftracker.domain.model import SourceOfStock, SourceType, Batch, BatchType, Species
from leaftracker.service_layer.unit_of_work import UnitOfWork


class ServiceError(RuntimeError):
    pass


class InvalidSource(Exception):
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
            raise InvalidSource(f"No such source: {source_reference}")

        reference = uow.batches().add(
            Batch(
                source_reference=source_reference,
                batch_type=BatchType(batch_type),
            )
        )

        uow.commit()

    return reference


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
        uow.commit()
