import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, Gtk


def on_activate(app):
    pass
    # win = NestingWindow(application=app)
    # win.present()


app = Adw.Application(application_id='org.bswa.jhanarato.LeafTracker')
app.connect('activate', on_activate)

app.run(None)