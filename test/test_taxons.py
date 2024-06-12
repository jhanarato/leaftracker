from leaftracker.domain.model import TaxonHistory, TaxonName


class TestTaxonName:
    def test_should_be_equal(self):
        name_one = TaxonName(genus="Acacia", species="saligna")
        name_two = TaxonName(genus="Acacia", species="saligna")

        assert name_one == name_two


class TestTaxonHistory:
    def test_should_have_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        assert taxon.current() == TaxonName(genus="Baumea", species="juncea")

    def test_should_change_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        taxon.new_name("Machaerina juncea")
        assert taxon.current() == TaxonName(genus="Machaerina", species="juncea")

    def test_should_list_other_names(self):
        taxon = TaxonHistory()
        taxon.new_name("Genus speciesone")
        taxon.new_name("Genus speciestwo")
        taxon.new_name("Genus speciesthree")

        assert taxon.not_current() == [
            TaxonName("Genus", "speciesone"),
            TaxonName("Genus", "speciestwo"),
        ]
