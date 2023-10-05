from revegetator.domain.model import Source, SourceType, Batch, BatchType
from revegetator.service_layer.unit_of_work import UnitOfWork


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


def add_order(source_name: str, uow: UnitOfWork):
    with uow:
        batchref = uow.batches().add(
            Batch(
                source_name=source_name,
                batch_type=BatchType.ORDER
            )
        )
        uow.commit()
    return batchref
