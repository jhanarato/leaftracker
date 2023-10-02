from datetime import date

import pytest

from revegetator.domain.model import Batch, Stock

@pytest.fixture
def species_names():
    return ["Banksia littoralis", "Hakea varia", "Hypocalymma angustifolium"]


@pytest.fixture
def batch_of_three(species_names):
    batch = Batch(
        reference="trillion-trees-2020-05-15",
        origin="Trillion Trees",
        date_received=date(2020, 5, 15)
    )

    for species in species_names:
        batch.add(
            Stock(
                species=species,
                quantity=20,
                size="tube"
            )
        )

    return batch


def test_should_add_stock_to_batch():
    batch = Batch(
        reference="trillion-trees-2020-05-15",
        origin="Trillion Trees",
        date_received=date(2020, 5, 15)
    )

    stock = Stock(
        species="Banksia littoralis",
        quantity=20,
        size="tube"
    )

    assert batch.quantity("Banksia littoralis") == 0

    batch.add(stock)

    assert batch.quantity("Banksia littoralis") == 20

    batch.add(stock)

    assert batch.quantity("Banksia littoralis") == 40


def test_should_get_species_list_from_batch(species_names, batch_of_three):
    assert set(batch_of_three.species()) == set(species_names)


def test_should_get_species_quantity(batch_of_three):
    assert batch_of_three.quantity("Banksia littoralis") == 20
