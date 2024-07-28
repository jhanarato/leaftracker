import pytest

from fakes import FakeSpeciesRepository, FakeUnitOfWork
from leaftracker.domain.model import Batch, BatchType, Stock, StockSize, TaxonName
from leaftracker.service_layer import services
from leaftracker.service_layer.services import InvalidSource, add_species, rename_species, ServiceError
from leaftracker.service_layer.unit_of_work import UnitOfWork


@pytest.fixture
def uow() -> UnitOfWork:
    return FakeUnitOfWork()


def test_should_catalogue_batch(uow):
    with uow:
        batch = Batch(
            source_reference="source-0001",
            batch_type=BatchType.PICKUP
        )

        batch.add(Stock(species_ref="Acacia saligna", quantity=20, size=StockSize.TUBE))

        ref = uow.batches().add(batch)
        uow.commit()

        new_batch = uow.batches().get(ref)

    assert new_batch.source_reference == "source-0001"
    assert new_batch.species() == ["Acacia saligna"]


def test_add_order(uow, program):
    ref = services.add_batch(program, "order", uow)

    assert ref == "batch-0001"

    assert uow.batches().get(ref).batch_type == BatchType.ORDER


def test_missing_source(uow):
    with pytest.raises(InvalidSource, match="No such source: Rodeo Nursery"):
        services.add_batch("Rodeo Nursery", "nursery", uow)


@pytest.fixture
def nursery(uow) -> str:
    return services.add_source_of_stock("Natural Area", "nursery", uow)


@pytest.fixture
def program(uow) -> str:
    return services.add_source_of_stock("Habitat Links", "program", uow)


def test_add_species(uow):
    reference = add_species("Acacia saligna", uow)
    assert reference == "species-0001"


def test_rename_species():
    uow = FakeUnitOfWork()
    reference = add_species("Baumea juncea", uow)
    assert reference == "species-0001"
    species = uow.species().get("species-0001")
    assert species.taxon_history.current() == TaxonName("Baumea juncea")  # type: ignore
    rename_species("species-0001", "Machaerina juncea", uow)
    species = uow.species().get("species-0001")
    assert species.taxon_history.current() == TaxonName("Machaerina juncea")  # type: ignore


def test_reference_not_assigned_when_adding_species():
    def none_reference():
        yield None

    uow = FakeUnitOfWork()
    repository = FakeSpeciesRepository()
    repository.references = none_reference()
    uow.set_species(repository)

    with pytest.raises(ServiceError):
        _ = add_species("Baumea juncea", uow)


def test_rename_non_existent_species():
    uow = FakeUnitOfWork()

    with pytest.raises(ServiceError):
        rename_species("xyz", "Machaerina juncea", uow)
