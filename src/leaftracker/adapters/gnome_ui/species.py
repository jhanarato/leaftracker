import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk


@Gtk.Template(filename="templates/species_dialog.ui")
class SpeciesDialog(Adw.ApplicationWindow):
    __gtype_name__ = "SpeciesDialog"

    @Gtk.Template.Callback()
    def cancel(self, button):
        print("Cancelled")
        self.close()

    @Gtk.Template.Callback()
    def add(self, button):
        print("Added")
        self.close()
