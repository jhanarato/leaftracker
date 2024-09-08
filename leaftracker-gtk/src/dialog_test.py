import gi

# gi.require_version('Gtk', '4.14')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/org/bswa/jhanarato/Leaftracker/dialog_test.ui")
class DialogTest(Adw.PreferencesDialog):
    __gtype_name__ = "DialogTest"
