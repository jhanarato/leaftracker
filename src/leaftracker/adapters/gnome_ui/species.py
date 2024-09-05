import gi

from leaftracker.adapters.elastic.unit_of_work import ElasticUnitOfWork
from leaftracker.service_layer import services

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk


@Gtk.Template(filename="templates/species_form.ui")
class SpeciesForm(Adw.PreferencesPage):
    __gtype_name__ = "SpeciesForm"

    def get_name(self):
        return "Acacia saligna"


@Gtk.Template(filename="templates/species_dialog.ui")
class SpeciesDialog(Adw.ApplicationWindow):
    __gtype_name__ = "SpeciesDialog"

    species_form: SpeciesForm = Gtk.Template.Child()

    def __init__(self, application: Adw.Application, uow: ElasticUnitOfWork):
        super().__init__(application=application)
        self._uow = uow

    @Gtk.Template.Callback()
    def cancel(self, button):
        self.close()

    @Gtk.Template.Callback()
    def apply(self, button):
        services.add_species(self.species_form.get_name(), self._uow)
        self.close()
