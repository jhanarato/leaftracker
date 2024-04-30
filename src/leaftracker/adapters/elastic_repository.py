from elasticsearch import Elasticsearch

from leaftracker.domain.model import Species


class SpeciesRepository:
    def __init__(self):
        self.es = Elasticsearch(hosts="http://localhost:9200")

    def add(self, species: Species) -> str:
        self.es.index(
            index="species",
            id=species.reference,
            document={
                "genus": species.names[0].genus,
                "species": species.names[0].genus,
            }
        )
        return species.reference

    def get(self, species_ref: str) -> Species:
        pass

