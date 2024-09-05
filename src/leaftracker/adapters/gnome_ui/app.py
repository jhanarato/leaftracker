import gi

from leaftracker.adapters.elastic.elasticsearch import Lifecycle, DocumentStore
from leaftracker.adapters.elastic.repositories.batch import BATCH_INDEX, BATCH_MAPPINGS, ElasticBatchRepository
from leaftracker.adapters.elastic.repositories.source_of_stock import SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS, \
    ElasticSourceOfStockRepository
from leaftracker.adapters.elastic.repositories.species import SPECIES_INDEX, SPECIES_MAPPINGS, ElasticSpeciesRepository
from leaftracker.adapters.elastic.unit_of_work import ElasticUnitOfWork

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from leaftracker.adapters.gnome_ui.species import SpeciesDialog


def create_indexes() -> None:
    Lifecycle(SPECIES_INDEX, SPECIES_MAPPINGS).create()
    Lifecycle(SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS).create()
    Lifecycle(BATCH_INDEX, BATCH_MAPPINGS).create()


def unit_of_work() -> ElasticUnitOfWork:
    return ElasticUnitOfWork(
        ElasticSourceOfStockRepository(DocumentStore(SOURCE_OF_STOCK_INDEX)),
        ElasticSpeciesRepository(DocumentStore(SPECIES_INDEX)),
        ElasticBatchRepository(DocumentStore(BATCH_INDEX)),
    )


def on_activate(app):
    species_dialog = SpeciesDialog(application=app, uow=unit_of_work())
    species_dialog.present()


def main():
    create_indexes()
    app = Adw.Application(application_id='org.bswa.jhanarato.LeafTracker')
    app.connect('activate', on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
