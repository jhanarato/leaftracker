import gi

from integration.test_elasticsearch import lifecycle
from leaftracker.adapters.elastic.elasticsearch import Lifecycle
from leaftracker.adapters.elastic.repositories.species import SPECIES_INDEX, SPECIES_MAPPINGS

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk

from leaftracker.adapters.gnome_ui.species import SpeciesDialog


def create_indexes():
    Lifecycle(SPECIES_INDEX, SPECIES_MAPPINGS).create()


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
