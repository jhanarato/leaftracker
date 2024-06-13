import pytest

from leaftracker.domain.model import TaxonHistory, TaxonName


class TestTaxonName:
    def test_should_be_equal(self):
        name_one = TaxonName("Acacia saligna")
        name_two = TaxonName("Acacia saligna")

        assert name_one == name_two

    def test_should_create_from_string(self):
        taxon = TaxonName("Acacia saligna")
        assert taxon.genus == "Acacia"
        assert taxon.species == "saligna"

    def test_should_cast_to_string(self):
        taxon = TaxonName("Acacia saligna")
        assert str(taxon) == "Acacia saligna"

    @pytest.mark.parametrize(
        "original,capitalised",
        [
            ("Acacia saligna", "Acacia saligna"),
        ]
    )
    def test_should_capitalise_genus_but_not_species(self, original, capitalised):
        taxon = TaxonName(original)
        assert str(taxon) == capitalised


class TestTaxonHistory:
    def test_should_have_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        assert taxon.current() == TaxonName("Baumea juncea")

    def test_should_change_current_name(self):
        taxon = TaxonHistory()
        taxon.new_name("Baumea juncea")
        taxon.new_name("Machaerina juncea")
        assert taxon.current() == TaxonName("Machaerina juncea")

    def test_should_list_other_names(self):
        taxon = TaxonHistory()
        taxon.new_name("Genus speciesone")
        taxon.new_name("Genus speciestwo")
        taxon.new_name("Genus speciesthree")

        assert taxon.not_current() == [
            TaxonName("Genus speciesone"),
            TaxonName("Genus speciestwo"),
        ]
