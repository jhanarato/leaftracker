import gi
# gi.require_version('Gtk', '4.14')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk


@Gtk.Template(resource_path="/org/bswa/jhanarato/Leaftracker/window_test.ui")
class WindowTest(Adw.ApplicationWindow):
    __gtype_name__ = "WindowTest"

    def __init__(self, application: Adw.Application):
        super().__init__(application=application)
