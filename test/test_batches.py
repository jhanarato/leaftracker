from datetime import date

import pytest

from revegetator.domain.model import Batch, Stock

BANKSIA = "Banksia littoralis"
HAKEA = "Hakea varia"
HYPOCALYMNA = "Hypocalymma angustifolium"


@pytest.fixture
def species_names():
    return [BANKSIA, HAKEA, HYPOCALYMNA]


@pytest.fixture
def batch():
    return Batch(
        reference="trillion-trees-2020-05-15",
        origin="Trillion Trees",
        date_received=date(2020, 5, 15)
    )


@pytest.fixture
def batch_of_three(batch, species_names):
    for species in species_names:
        batch.add(Stock(species=species, quantity=20, size="tube"))

    return batch


def test_should_combine_quantities_of_same_stock(batch):
    stock = Stock(species=BANKSIA, quantity=20, size="tube")

    batch.add(stock)
    batch.add(stock)
    assert batch.quantity(BANKSIA) == 40


def test_should_get_species_list_from_batch(species_names, batch_of_three):
    assert set(batch_of_three.species()) == set(species_names)


def test_should_get_species_quantity(batch_of_three):
    assert batch_of_three.quantity(BANKSIA) == 20


def test_should_give_quantity_of_sized_stock(batch):
    batch.add(Stock(species=BANKSIA, quantity=20, size="tube"))
    batch.add(Stock(species=BANKSIA, quantity=10, size="pot"))

    assert batch.quantity(BANKSIA, size="tube") == 20
    assert batch.quantity(BANKSIA, size="pot") == 10


def test_should_identify_batch_after_modification():
    a_batch = Batch(
        reference="batch-a",
        origin="Trillion Trees",
        date_received=date(2020, 5, 15),
    )

    same_batch_modified = Batch(
        reference="batch-a",
        origin="Origin Different",
        date_received=date(2020, 5, 16)
    )

    same_batch_modified.add(Stock(species=BANKSIA, quantity=20, size="tube"))

    assert a_batch == same_batch_modified
    assert hash(a_batch) == hash(same_batch_modified)
    assert len({a_batch, same_batch_modified}) == 1
