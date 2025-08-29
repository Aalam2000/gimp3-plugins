#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gimp", "3.0")
gi.require_version("GimpUi", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Gimp, GLib, Gtk, GimpUi, Pango
import sys, os


class ProjectInspector(Gimp.PlugIn):
    __gtype_name__ = "project_inspector_g3"

    # Регистрируем процедуру
    def do_query_procedures(self):
        return ["plug-in-project-inspector-g3"]

    # Создаём процедуру в стиле примера Goat (GIMP 3)
    def do_create_procedure(self, name):
        proc = Gimp.ImageProcedure.new(
            self, name,
            Gimp.PDBProcType.PLUGIN,
            self.run, None
        )
        proc.set_image_types("*")
        # proc.set_sensitivity_mask(Gimp.ProcedureSensitivityMask.DRAWABLE)

        proc.set_menu_label("Project Inspector (fonts & layers)…")
        # Кладём кнопку туда же, где и пример Goat:
        proc.add_menu_path("<Image>/Filters/Development/")

        proc.set_documentation(
            "Fonts/Layers report",
            "List fonts used in text layers and count layers",
            name
        )
        proc.set_attribution("you", "you", "2025")
        return proc

    @staticmethod
    def show_report(title: str, text: str):
        GimpUi.init("project-inspector-g3")
        dlg = Gtk.Dialog(title=title, flags=0)
        dlg.set_default_size(640, 420)

        box = dlg.get_content_area()

        # Экранируем заголовок (Gtk.utils_escape не существует)
        header = Gtk.Label(label=f"<b>{GLib.markup_escape_text(title)}</b>")
        header.set_use_markup(True)
        header.set_xalign(0.0)
        box.pack_start(header, False, False, 6)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        box.pack_start(scrolled, True, True, 6)

        tv = Gtk.TextView()
        tv.set_editable(False)
        tv.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        tv.override_font(Pango.FontDescription("Monospace 10"))
        buf_ = tv.get_buffer()
        buf_.set_text(text)
        scrolled.add(tv)

        dlg.add_button("_OK", Gtk.ResponseType.OK)
        dlg.show_all()
        dlg.run()
        dlg.destroy()

    # Сигнатура как у примера Goat: image + drawables + config + run_data
    def run(self, procedure, run_mode, image, drawables, config, run_data):
        # Gimp.message("Project Inspector: start")

        total = 0
        visible = 0
        hidden = 0
        groups = 0
        texts = 0
        fonts = set()
        names = []

        def walk(item):
            nonlocal total, visible, hidden, groups, texts
            if isinstance(item, Gimp.GroupLayer):
                groups += 1
                names.append(f"[Group] {item.get_name()}")
                for ch in item.get_children():
                    walk(ch)
                return

            # обычный слой
            total += 1
            if item.get_visible():
                visible += 1
            else:
                hidden += 1

            # текстовый слой -> шрифт
            if isinstance(item, Gimp.TextLayer):
                texts += 1
                try:
                    f = item.get_font()  # GIMP-3 API
                    if f:
                        try:
                            name = f.get_name() if hasattr(f, "get_name") else f.props.name
                        except Exception:
                            name = str(f)
                        if name:
                            fonts.add(name)
                except Exception:
                    pass
                names.append(f"[Text] {item.get_name()}")
            else:
                names.append(item.get_name())

        # стартуем от верхних узлов
        for top in image.get_layers():
            walk(top)

        report = (
                f"All layers: {total} | visible: {visible} | hidden: {hidden} | "
                f"groups: {groups} | text layers: {texts}\n"
                "Fonts:\n" + ("\n".join(f"  • {f}" for f in sorted(fonts)) if fonts else "  — none")
        )
        self.show_report("Project Inspector", report)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


Gimp.main(ProjectInspector.__gtype__, sys.argv)
