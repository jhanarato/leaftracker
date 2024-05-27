import pytest

from conftest import FakeUnitOfWork


def test_should_rollback_if_not_committed(saligna):
    uow = FakeUnitOfWork()

    with uow:
        uow.species().add(saligna)

    assert saligna.reference is None


@pytest.mark.skip("Dealing with another issue right now.")
def test_should_assign_reference_on_commit(saligna):
    uow = FakeUnitOfWork()

    with uow:
        uow.species().add(saligna)
        uow.commit()

    assert saligna.reference == "species-001"
