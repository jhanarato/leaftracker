from leaftracker.domain.model import Species, ScientificName


class TestSpeciesRepository:
    def test_add(self):
        name = ScientificName(
            genus="Acacia",
            species="Saligna",
            is_most_recent=True
        )

        species = Species("acacia-saligna", name)
