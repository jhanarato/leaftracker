import gi

from leaftracker.adapters.elastic.elasticsearch import Lifecycle
from leaftracker.adapters.elastic.repositories.batch import BATCH_INDEX, BATCH_MAPPINGS
from leaftracker.adapters.elastic.repositories.source_of_stock import SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS
from leaftracker.adapters.elastic.repositories.species import SPECIES_INDEX, SPECIES_MAPPINGS

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from leaftracker.adapters.gnome_ui.species import SpeciesDialog


def create_indexes():
    Lifecycle(SPECIES_INDEX, SPECIES_MAPPINGS).create()
    Lifecycle(SOURCE_OF_STOCK_INDEX, SOURCE_OF_STOCK_MAPPINGS).create()
    Lifecycle(BATCH_INDEX, BATCH_MAPPINGS).create()


def on_activate(app):
    species_dialog = SpeciesDialog(application=app)
    species_dialog.present()


def main():
    create_indexes()
    app = Adw.Application(application_id='org.bswa.jhanarato.LeafTracker')
    app.connect('activate', on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
