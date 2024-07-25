import pytest

from fakes import FakeUnitOfWork, FakeSourceOfStockRepository
from leaftracker.domain.model import SourceType
from leaftracker.service_layer import services


@pytest.fixture
def uow() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    uow._sources = FakeSourceOfStockRepository()
    return uow


def test_add_nursery(uow):
    reference = services.add_nursery("Trillion Trees", uow)
    assert uow.sources().get(reference).source_type == SourceType.NURSERY


def test_add_program(uow):
    reference = services.add_program("Habitat Links", uow)
    assert uow.sources().get(reference).source_type == SourceType.PROGRAM
