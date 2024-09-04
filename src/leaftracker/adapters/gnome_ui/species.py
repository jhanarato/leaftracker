import gi

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

    @Gtk.Template.Callback()
    def cancel(self, button):
        print("Cancelled")
        self.close()

    @Gtk.Template.Callback()
    def apply(self, button):
        print(self.species_form.get_name())
        self.close()
