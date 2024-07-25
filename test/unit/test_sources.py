from leaftracker.domain.model import SourceType
from leaftracker.service_layer import services
from unit.fakes import FakeUnitOfWork


def test_new_source_of_stock():
    uow = FakeUnitOfWork()
    reference = services.add_source_of_stock("Habitat Links", "nursery", uow)
