from leaftracker.domain.model import TaxonHistory, TaxonName


def test_should_have_current_name():
    taxon = TaxonHistory()
    taxon.new_name("Baumea juncea")
    assert taxon.current() == TaxonName(genus="Baumea", species="juncea")


def test_should_change_current_name():
    taxon = TaxonHistory()
    taxon.new_name("Baumea juncea")
    taxon.new_name("Machaerina juncea")
    assert taxon.current() == TaxonName(genus="Machaerina", species="juncea")


def test_should_list_other_names():
    taxon = TaxonHistory()
    taxon.new_name("Genus speciesone")
    taxon.new_name("Genus speciestwo")
    taxon.new_name("Genus speciesthree")

    assert taxon.not_current() == [
        TaxonName("Genus", "speciesone"),
        TaxonName("Genus", "speciestwo"),
    ]
