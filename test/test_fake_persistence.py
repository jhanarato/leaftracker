from conftest import FakeUnitOfWork, FakeSpeciesRepository


class TestFakeUnitOfWork:
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

    def test_should_retrieve_species_after_commit(self, saligna):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)
            uow.commit()

        retrieved = uow.species().get(saligna.reference)
        assert retrieved.reference == "species-0001"  # type: ignore

    def test_should_discard_uncommitted_species_on_rollback(self, saligna, dentifera):
        uow = FakeUnitOfWork()

        with uow:
            uow.species().add(saligna)

        with uow:
            uow.species().add(dentifera)
            uow.commit()

        retrieved = uow.species().get("species-0001")
        assert retrieved.taxon_history.current().species == "dentifera"  # type: ignore


class TestFakeSpeciesRepository:
    def test_should_return_none_when_missing(self):
        assert FakeSpeciesRepository().get("missing") is None


class FakeLifecycle:
    def __init__(self, exists: bool):
        self._exists = exists

    def create(self) -> None:
        self._exists = True

    def delete(self) -> None:
        self._exists = False

    def exists(self) -> bool:
        return self._exists

    def refresh(self) -> None:
        pass


class TestFakeLifecycle:
    def test_create_when_does_not_exist(self):
        lc = FakeLifecycle(exists=False)
        lc.create()
        assert lc.exists()

    def test_create_when_exists(self):
        lc = FakeLifecycle(exists=True)
        lc.create()
        assert lc.exists()

    def test_delete_when_does_not_exist(self):
        lc = FakeLifecycle(exists=False)
        lc.delete()
        assert not lc.exists()

    def test_delete_when_exists(self):
        lc = FakeLifecycle(exists=True)
        lc.delete()
        assert not lc.exists()
