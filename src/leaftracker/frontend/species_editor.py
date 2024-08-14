import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title='Edit Species')


def on_activate(app):
    win = MyWindow(application=app)
    win.present()


def main():
    app = Gtk.Application(application_id='org.bswa.LeafTracker')
    app.connect('activate', on_activate)
    app.run(None)


if __name__ == "__main__":
    main()
