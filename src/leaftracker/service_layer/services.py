from leaftracker.domain.model import Source, SourceType, Batch, BatchType, Species, ScientificName
from leaftracker.service_layer.unit_of_work import UnitOfWork


class InvalidSource(Exception):
    pass


def add_nursery(name: str, uow: UnitOfWork):
    with uow:
        source = Source(name, SourceType.NURSERY)
        uow.sources().add(source)
        uow.commit()


def add_program(name: str, uow: UnitOfWork):
    with uow:
        source = Source(name, SourceType.PROGRAM)
        uow.sources().add(source)
        uow.commit()


def _add_batch(source_name: str, batch_type: BatchType, uow: UnitOfWork) -> str:
    with uow:
        source = uow.sources().get(source_name)

        if not source:
            raise InvalidSource(f"No such source: {source_name}")

        batchref = uow.batches().add(
            Batch(
                source=source,
                batch_type=batch_type
            )
        )
        uow.commit()

    return batchref


def add_order(source_name: str, uow: UnitOfWork) -> str:
    return _add_batch(source_name, BatchType.ORDER, uow)


def add_delivery(source_name: str, uow: UnitOfWork) -> str:
    return _add_batch(source_name, BatchType.DELIVERY, uow)


def add_pickup(source_name: str, uow: UnitOfWork) -> str:
    return _add_batch(source_name, BatchType.PICKUP, uow)


def add_species(genus: str, species: str, uow: UnitOfWork) -> str:
    species = Species(
        ScientificName(genus=genus, species=species)
    )

    with uow:
        uow.species().add(species)
        uow.commit()

    return species.reference


def rename_species(reference: str, genus: str, species: str, uow: UnitOfWork) -> None:
    new_name = ScientificName(genus=genus, species=species)

    with uow:
        species = uow.species().get(reference)
        species.new_scientific_name(new_name)
        uow.commit()
