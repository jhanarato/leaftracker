import pytest

from fakes import FakeBatchRepository, FakeSpeciesRepository, FakeUnitOfWork
from leaftracker.adapters.repository import BatchRepository
from leaftracker.domain.model import Batch, Source, SourceType, BatchType, Stock, StockSize, TaxonName
from leaftracker.service_layer import services
from leaftracker.service_layer.services import InvalidSource, add_species, rename_species, ServiceError
from leaftracker.service_layer.unit_of_work import UnitOfWork


def test_fake_reference():
    repo: BatchRepository = FakeBatchRepository([])

    references = [repo.add(Batch(Source("Habitat Links", SourceType.PROGRAM), BatchType.DELIVERY)),
                  repo.add(Batch(Source("Habitat Links", SourceType.PROGRAM), BatchType.DELIVERY)),
                  repo.add(Batch(Source("Natural Area", SourceType.NURSERY), BatchType.DELIVERY))]

    assert references == ["batch-0001", "batch-0002", "batch-0003"]


@pytest.fixture
def uow() -> UnitOfWork:
    return FakeUnitOfWork()


def test_should_catalogue_batch(uow):
    with uow:
        batch = Batch(
            source=Source("Trillion Trees", SourceType.NURSERY),
            batch_type=BatchType.PICKUP
        )

        batch.add(Stock(species_ref="Acacia saligna", quantity=20, size=StockSize.TUBE))

        ref = uow.batches().add(batch)
        uow.commit()

        new_batch = uow.batches().get(ref)

    assert new_batch.source == Source("Trillion Trees", SourceType.NURSERY)
    assert new_batch.species() == ["Acacia saligna"]


def test_add_nursery(uow):
    services.add_nursery("Trillion Trees", uow)
    assert uow.sources().get("Trillion Trees").source_type == SourceType.NURSERY


def test_add_program(uow):
    services.add_program("Habitat Links", uow)
    assert uow.sources().get("Habitat Links").source_type == SourceType.PROGRAM


def test_add_order(uow):
    program = "Habitat Links"
    services.add_program(program, uow)
    ref = services.add_order(program, uow)

    assert ref == "batch-0001"

    assert uow.batches().get(ref).batch_type == BatchType.ORDER


def test_missing_source(uow):
    with pytest.raises(InvalidSource, match="No such source: Rodeo Nursery"):
        services.add_order("Rodeo Nursery", uow)


@pytest.fixture
def nursery(uow) -> Source:
    nursery = "Natural Area"
    services.add_nursery(nursery, uow)

    with uow:
        return uow.sources().get(nursery)


@pytest.fixture
def program(uow) -> Source:
    program = "Habitat Links"
    services.add_program(program, uow)

    with uow:
        return uow.sources().get(program)


def test_add_delivery(uow, program):
    ref = services.add_delivery(program.name, uow)
    assert uow.batches().get(ref).batch_type == BatchType.DELIVERY


def test_add_pickup(uow, nursery):
    ref = services.add_pickup(nursery.name, uow)
    assert uow.batches().get(ref).batch_type == BatchType.PICKUP


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
