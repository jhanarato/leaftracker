import pytest

from conftest import FakeUnitOfWork, FakeSpeciesRepository


class TestUnitOfWork:
    def test_should_rollback_if_not_committed(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)

        assert saligna.reference is None

    def test_should_assign_reference_on_commit(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)
            uow.commit()

        assert saligna.reference == "species-0001"
