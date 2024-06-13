from leaftracker.domain.model import TaxonHistory, TaxonName


class TestTaxonName:
    def test_should_be_equal(self):
        name_one = TaxonName.from_string("Acacia saligna")
        name_two = TaxonName.from_string("Acacia saligna")

        assert name_one == name_two

    def test_should_create_from_string(self):
        taxon = TaxonName.from_string("Acacia saligna")
        assert taxon.genus == "Acacia"
        assert taxon.species == "saligna"


class TestTaxonHistory:
    def test_should_have_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        assert taxon.current() == TaxonName.from_string("Baumea juncea")

    def test_should_change_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        taxon.new_name("Machaerina juncea")
        assert taxon.current() == TaxonName.from_string("Machaerina juncea")

    def test_should_list_other_names(self):
        taxon = TaxonHistory()
        taxon.new_name("Genus speciesone")
        taxon.new_name("Genus speciestwo")
        taxon.new_name("Genus speciesthree")

        assert taxon.not_current() == [
            TaxonName.from_string("Genus speciesone"),
            TaxonName.from_string("Genus speciestwo"),
        ]
