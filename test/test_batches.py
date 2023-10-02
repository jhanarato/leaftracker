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

    batch.add(stock)

    assert batch.stock["Banksia littoralis"] == 20
