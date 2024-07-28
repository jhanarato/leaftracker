import pytest

from leaftracker.domain.model import Batch, Stock, SourceOfStock, StockSize, BatchType, SourceType

BANKSIA = "Banksia littoralis"
HAKEA = "Hakea varia"
HYPOCALYMNA = "Hypocalymma angustifolium"


@pytest.fixture
def species_names():
    return [BANKSIA, HAKEA, HYPOCALYMNA]


@pytest.fixture
def batch():
    return Batch(
        source_reference="source-0001",
        batch_type=BatchType.DELIVERY,
        reference="batch-0001")


@pytest.fixture
def batch_of_three(batch, species_names):
    for species in species_names:
        batch.add(Stock(species_ref=species, quantity=20, size=StockSize.TUBE))

    return batch


def test_should_combine_quantities_of_same_stock(batch):
    stock = Stock(species_ref=BANKSIA, quantity=20, size=StockSize.TUBE)

    batch.add(stock)
    batch.add(stock)
    assert batch.quantity(BANKSIA) == 40


def test_should_get_species_list_from_batch(species_names, batch_of_three):
    assert set(batch_of_three.species()) == set(species_names)


def test_should_get_species_quantity(batch_of_three):
    assert batch_of_three.quantity(BANKSIA) == 20


def test_should_give_quantity_of_sized_stock(batch):
    batch.add(Stock(species_ref=BANKSIA, quantity=20, size=StockSize.TUBE))
    batch.add(Stock(species_ref=BANKSIA, quantity=10, size=StockSize.POT))

    assert batch.quantity_of_size(BANKSIA, StockSize.TUBE) == 20
    assert batch.quantity_of_size(BANKSIA, StockSize.POT) == 10


def test_should_identify_batch_after_modification():
    same_reference = "batch-0001"
    a_batch = Batch(
        source_reference="source-0001",
        batch_type=BatchType.PICKUP,
        reference=same_reference
    )

    same_batch_modified = Batch(
        source_reference="source-0001",
        batch_type=BatchType.PICKUP,
        reference=same_reference)

    same_batch_modified.add(Stock(species_ref=BANKSIA, quantity=20, size=StockSize.TUBE))

    assert a_batch == same_batch_modified
    assert hash(a_batch) == hash(same_batch_modified)
    assert len({a_batch, same_batch_modified}) == 1
