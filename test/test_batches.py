from datetime import date

from revegetator.domain.model import Batch, Stock


def test_should_create_batch_with_single_species():
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

    assert batch.quantity["Banksia littoralis"] == 0

    batch.add(stock)

    assert batch.quantity["Banksia littoralis"] == 20

    batch.add(stock)

    assert batch.quantity["Banksia littoralis"] == 40


def test_should_get_species_list_from_batch():
    batch = Batch(
        reference="trillion-trees-2020-05-15",
        origin="Trillion Trees",
        date_received=date(2020, 5, 15)
    )

    species_in_batch = ["Banksia littoralis", "Hakea varia", "Hypocalymma angustifolium"]

    for species in species_in_batch:
        batch.add(
            Stock(
                species=species,
                quantity=20,
                size="tube"
            )
        )

    assert set(batch.species()) == set(species_in_batch)
