import pytest

from fakes import FakeSpeciesRepository, FakeUnitOfWork
from leaftracker.domain.model import BatchType, TaxonName, SourceType
from leaftracker.service_layer import services
from leaftracker.service_layer.services import NotFoundError, ServiceError


def test_add_source_of_stock(uow):
    reference = services.add_source_of_stock("Trillion Trees", "nursery", uow)
    retrieved = uow.sources().get(reference)
    assert retrieved is not None
    assert retrieved.source_type == SourceType.NURSERY


def test_add_stock():
    uow = FakeUnitOfWork()

    source_ref = services.add_source_of_stock("Trillion Trees", "nursery", uow)
    species_ref = services.add_species("Acacia saligna", uow)
    batch_ref = services.add_batch(source_ref, "order", uow)

    services.add_stock(batch_ref, species_ref, 20, "tube", uow)

    with uow:
        batch = uow.batches().get(batch_ref)
        assert batch is not None
        assert batch.quantity(species_ref) == 20


def test_add_stock_to_missing_batch(uow):
    species_ref = services.add_species("Acacia saligna", uow)
    with pytest.raises(NotFoundError, match="No batch with reference batch-xxxx"):
        services.add_stock("batch-xxxx", species_ref, 20, "tube", uow)


def test_add_stock_with_missing_species():
    uow = FakeUnitOfWork()
    source_ref = services.add_source_of_stock("Trillion Trees", "nursery", uow)
    batch_ref = services.add_batch(source_ref, "order", uow)

    with pytest.raises(NotFoundError, match="No species with reference species-xxxx"):
        services.add_stock(batch_ref, "species-xxxx", 20, "tube", uow)


def test_add_order():
    uow = FakeUnitOfWork()
    source_reference = services.add_source_of_stock("Habitat Links", "program", uow)
    batch_reference = services.add_batch(source_reference, "order", uow)
    assert batch_reference == "batch-0001"
    assert uow.batches().get(batch_reference).batch_type == BatchType.ORDER


def test_add_batch_with_missing_source(uow):
    with pytest.raises(NotFoundError, match="No source with reference source-0001"):
        services.add_batch("source-0001", "nursery", uow)


def test_add_species(uow):
    reference = services.add_species("Acacia saligna", uow)
    assert reference == "species-0001"


def test_rename_species():
    uow = FakeUnitOfWork()
    reference = services.add_species("Baumea juncea", uow)
    assert reference == "species-0001"
    species = uow.species().get("species-0001")
    assert species.taxon_history.current() == TaxonName("Baumea juncea")  # type: ignore
    services.rename_species("species-0001", "Machaerina juncea", uow)
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
        _ = services.add_species("Baumea juncea", uow)


def test_rename_non_existent_species():
    uow = FakeUnitOfWork()

    with pytest.raises(ServiceError):
        services.rename_species("xyz", "Machaerina juncea", uow)
