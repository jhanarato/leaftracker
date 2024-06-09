from leaftracker.domain.model import TaxonHistory, TaxonName


def test_should_have_current_name():
    taxon = TaxonHistory()
    taxon.new_name("Baumea juncea")
    assert taxon.current_name() == TaxonName(genus="Baumea", species="juncea")


def test_should_change_current_name():
    taxon = TaxonHistory()
    taxon.new_name("Baumea juncea")
    taxon.new_name("Machaerina juncea")
    assert taxon.current_name() == TaxonName(genus="Machaerina", species="juncea")


def test_should_iterate_from_newest_to_oldest_name():
    taxon = TaxonHistory()
    taxon.new_name("Baumea juncea")
    taxon.new_name("Machaerina juncea")

    names = taxon.newest_to_oldest()

    assert next(names) == TaxonName(genus="Machaerina", species="juncea")
    assert next(names) == TaxonName(genus="Baumea", species="juncea")
