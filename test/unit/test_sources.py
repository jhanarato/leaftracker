from fakes import FakeUnitOfWork
from leaftracker.domain.model import SourceType
from leaftracker.service_layer import services


def test_add_nursery():
    uow = FakeUnitOfWork()
    reference = services.add_nursery("Trillion Trees", uow)
    assert uow.sources().get(reference).source_type == SourceType.NURSERY


def test_add_program():
    uow = FakeUnitOfWork()
    reference = services.add_program("Habitat Links", uow)
    assert uow.sources().get(reference).source_type == SourceType.PROGRAM
