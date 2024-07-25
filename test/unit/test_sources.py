from fakes import FakeUnitOfWork
from leaftracker.service_layer import services


def test_new_source_of_stock():
    uow = FakeUnitOfWork()
    reference = services.add_source_of_stock("Habitat Links", "nursery", uow)
