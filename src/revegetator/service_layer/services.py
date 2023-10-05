from revegetator.domain.model import Source, SourceType
from revegetator.service_layer.unit_of_work import UnitOfWork


def add_nursery(name: str, uow: UnitOfWork):
    with uow:
        source = Source(name, SourceType.NURSERY)
        uow.sources().add(source)
        uow.commit()
