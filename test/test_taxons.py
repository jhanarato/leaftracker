import pytest

from leaftracker.domain.model import TaxonHistory, TaxonName


@pytest.mark.parametrize(
    "species_name", [
        "Acacia saligna",
        "Hakea petiolaris trichophylla",
        "Adenanthos sericeus sericeus",
    ]
)
class TestTaxonName:
    def test_should_be_equal(self, species_name):
        name_one = TaxonName(species_name)
        name_two = TaxonName(species_name)

        assert name_one == name_two

    def test_should_cast_to_string(self, species_name):
        taxon = TaxonName(species_name)
        assert str(taxon) == species_name

    @pytest.mark.parametrize(
        "name",
        [
            "Acacia saligna", "acacia saligna",
            "acacia Saligna", "Acacia Saligna",
            "ACACIA SALIGNA", "aCaCiA SaLiGnA",
        ]
    )
    def test_should_capitalise_genus_but_not_species(self, name, species_name):
        taxon = TaxonName(name)
        assert str(taxon) == "Acacia saligna"


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
