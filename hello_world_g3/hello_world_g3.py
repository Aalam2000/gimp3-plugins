#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gimp", "3.0")
from gi.repository import Gimp, GLib, GObject

class HelloWorld(Gimp.PlugIn):

    def do_query_procedures(self):
        return ["plug-in-hello-world"]

    def do_create_procedure(self, name):
        procedure = Gimp.ImageProcedure.new(
            self, name, Gimp.PDBProcType.PLUGIN, self.run, None
        )
        procedure.set_image_types("*")
        procedure.set_menu_label("Hello World (Python3)")
        procedure.add_menu_path("<Image>/Filters/Test/")
        procedure.set_attribution("You", "You", "2025")
        return procedure

    def run(self, procedure, run_mode, image, n_drawables, drawables, config, data):
        message = "Hello from Python 3 GIMP plugin!"
        Gimp.message(message)
        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

Gimp.main(HelloWorld.__gtype__, sys.argv)
