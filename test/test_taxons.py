import pytest

from leaftracker.domain.model import TaxonHistory, TaxonName, MalformedTaxonName


class TestTaxonName:
    @pytest.mark.parametrize(
        "species_name", [
            "Acacia saligna",
            "Hakea petiolaris trichophylla",
            "Adenanthos sericeus sericeus",
        ]
    )
    def test_should_be_equal(self, species_name):
        name_one = TaxonName(species_name)
        name_two = TaxonName(species_name)

        assert name_one == name_two

    @pytest.mark.parametrize(
        "species_name", [
            "Acacia saligna",
            "Hakea petiolaris trichophylla",
            "Adenanthos sericeus sericeus",
        ]
    )
    def test_should_cast_to_string(self, species_name):
        taxon = TaxonName(species_name)
        assert str(taxon) == species_name

    @pytest.mark.parametrize(
        "species_name",
        [
            "Acacia saligna", "acacia saligna",
            "ACACIA saligna", "AcACiA saligna",
        ]
    )
    def test_should_capitalise_genus(self, species_name):
        taxon = TaxonName(species_name)
        assert str(taxon) == "Acacia saligna"

    @pytest.mark.parametrize(
        "species_name",
        [
            "Acacia Saligna", "acacia saligna",
            "Acacia SALIGNA", "Acacia SaLiGnA",
        ]
    )
    def test_should_lowercase_species(self, species_name):
        taxon = TaxonName(species_name)
        assert str(taxon) == "Acacia saligna"

    @pytest.mark.parametrize(
        "species_name",
        [
            "Hakea petiolaris trichophylla",
            "Hakea petiolaris Trichophylla",
            "Hakea petiolaris TRICHOPHYLLA",
            "Hakea petiolaris TrIcHoPhYlLa",
        ]
    )
    def test_should_lowercase_subspecies(self, species_name):
        taxon = TaxonName(species_name)
        assert str(taxon) == "Hakea petiolaris trichophylla"

    @pytest.mark.parametrize(
        "species_name", ["Hakea", "Hakea petiolaris trichophylla trichophylla"]
    )
    def test_should_flag_malformed_names(self, species_name):
        with pytest.raises(MalformedTaxonName):
            taxon = TaxonName(species_name)


class TestTaxonHistory:
    def test_should_initialize_with_current_name(self):
        taxon = TaxonHistory("Baumea juncea")
        assert taxon.current() == TaxonName("Baumea juncea")

    def test_should_change_current_name(self):
        taxon = TaxonHistory("Baumea juncea")
        taxon.new_current_name("Machaerina juncea")
        assert taxon.current() == TaxonName("Machaerina juncea")

    def test_should_add_previous_name(self):
        taxon = TaxonHistory("Machaerina juncea")
        taxon.add_previous_name("Baumea juncea")
        assert list(taxon.previous()) == [TaxonName("Baumea juncea")]

    def test_should_iterate_over_previous_before_current(self):
        taxon = TaxonHistory("Machaerina juncea")
        taxon.add_previous_name("Baumea juncea")
        assert list(taxon) == [TaxonName("Baumea juncea"), TaxonName("Machaerina juncea")]
