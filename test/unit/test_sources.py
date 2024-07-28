import pytest

from fakes import FakeUnitOfWork
from leaftracker.domain.model import SourceType
from leaftracker.service_layer import services


def test_add_source_of_stock():
    uow = FakeUnitOfWork()
    reference = services.add_source_of_stock("Trillion Trees", "nursery", uow)
    retrieved = uow.sources().get(reference)
    assert retrieved is not None
    assert retrieved.source_type == SourceType.NURSERY
