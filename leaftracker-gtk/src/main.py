# main.py
#
# Copyright 2024 JR
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import gi

# gi.require_version('Gtk', '4.14')
gi.require_version('Adw', '1')

from gi.repository import Adw, Gtk, Gio
from .window_test import WindowTest


def on_activate(app):
    window = WindowTest(application=app)
    window.present()


def main(version):
    app = Adw.Application(application_id='org.bswa.jhanarato.Leaftracker')
    app.connect('activate', on_activate)
    return app.run(sys.argv)
