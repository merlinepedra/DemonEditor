import os
from ftplib import FTP
from threading import Thread

import gi

from main.eparser import get_channels, get_satellites, get_bouquets, get_bouquet
from main.eparser.__constants import SERVICE_TYPE
from main.properties import get_config, write_config

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

__status_bar = None
__options = get_config()
__services_model = None
__bouquets_model = None
__fav_model = None
__services_view = None
__fav_view = None
__bouquets_view = None
__DATA_FILES_LIST = ("tv", "radio", "lamedb")
__channels = {}


def on_about_app(item):
    builder = Gtk.Builder()
    builder.add_from_file("editor_ui.glade")
    dialog = builder.get_object("about_dialog")
    dialog.run()
    dialog.destroy()


def get_handlers():
    return {
        "on_close_main_window": Gtk.main_quit,
        "on_about_app": on_about_app,
        "on_preferences": on_preferences,
        "on_download": on_download,
        "on_upload": on_upload,
        "on_data_dir_field_icon_press": on_path_open,
        "on_data_open": on_data_open,
        "on_tree_view_key_release": on_tree_view_key_release,
        "on_bouquets_selection": on_bouquets_selection,
        "on_satellite_editor_show": on_satellite_editor_show,
        "on_satellites_list_load": on_satellites_list_load,
        "on_services_selection": on_services_selection,
        "on_fav_selection": on_fav_selection,
        "on_up": on_up,
        "on_down": on_down,
        "on_cut": on_cut,
        "on_copy": on_copy,
        "on_paste": on_paste,
        "on_delete": on_delete
    }


def on_up(item):
    pass


def on_down(item):
    pass


def on_cut(item):
    pass


def on_copy(item):
    pass


def on_paste(item):
    pass


def on_delete(item):
    """ Delete selected items from views """
    for view in [__services_view, __fav_view, __bouquets_view]:
        selection = view.get_selection()
        store, paths = selection.get_selected_rows()
        itrs = []
        for path in paths:
            itrs.append(store.get_iter(path))
        for itr in itrs:
            store.remove(itr)


def on_satellite_editor_show(model):
    """ Shows satellites editor dialog """
    builder = Gtk.Builder()
    builder.add_from_file("editor_ui.glade")
    builder.connect_signals(get_handlers())
    dialog = builder.get_object("satellites_editor_dialog")
    dialog.run()
    dialog.destroy()


def on_satellites_list_load(model):
    """ Load satellites data into model """
    satellites = get_satellites(__options["data_dir_path"])
    model.clear()
    for name, flags, pos, transponders in satellites:
        parent = model.append(None, [name, *[None for x in range(9)]])
        for transponder in transponders:
            model.append(parent, ["Transponder:", *transponder])


def data_open(model):
    try:
        model.clear()
        __fav_model.clear()
        model_id = model.get_name()
        data_path = get_config()["data_dir_path"]
        if model_id == "services_list_store":
            for ch in get_channels(data_path + "lamedb"):
                #  adding channels to dict with fav_id as keys
                __channels[ch.fav_id] = ch
                model.append(ch)
        if model_id == "bouquets_tree_store":
            data = get_bouquets(data_path)
            for name, bouquets in data:
                parent = model.append(None, [name])
                for bouquet in bouquets:
                    model.append(parent, [bouquet])
    except Exception as e:
        __status_bar.push(1, getattr(e, "message", repr(e)))


def on_data_open(model):
    # Maybe is not necessary? Need testing.
    task = Thread(target=data_open(model))
    task.start()


def on_services_selection(model, path, column):
    delete_selection(__fav_view, __bouquets_view)


def on_fav_selection(model, path, column):
    delete_selection(__services_view, __bouquets_view)


def on_bouquets_selection(model, path, column):
    if len(path) > 1:
        delete_selection(__services_view)
        tree_iter = model.get_iter(path)
        name = model.get_value(tree_iter, 0)
        # 'tv' Temporary! It is necessary to implement a row type attribute.
        bq = get_bouquet(__options["data_dir_path"], name, SERVICE_TYPE[1].lower())
        __fav_model.clear()
        for num, ch_id in enumerate(bq):
            channel = __channels.get(ch_id, None)
            __fav_model.append((num + 1, channel[0], channel[2], channel[9]))


def delete_selection(view, *args):
    """ Used for clear selection on given view(s) """
    for v in [view, *args]:
        v.get_selection().unselect_all()


def on_path_open(*args):
    builder = Gtk.Builder()
    builder.add_from_file("editor_ui.glade")
    dialog = builder.get_object("path_chooser_dialog")
    response = dialog.run()
    if response == -12:  # for fix assertion 'gtk_widget_get_can_default (widget)' failed
        args[0].set_text(dialog.get_filename())
    dialog.destroy()


def on_preferences(item):
    builder = Gtk.Builder()
    builder.add_from_file("editor_ui.glade")
    builder.connect_signals(get_handlers())
    dialog = builder.get_object("settings_dialog")
    host_field = builder.get_object("host_field")
    host_field.set_text(__options["host"])
    port_field = builder.get_object("port_field")
    port_field.set_text(__options["port"])
    login_field = builder.get_object("login_field")
    login_field.set_text(__options["user"])
    password_field = builder.get_object("password_field")
    password_field.set_text(__options["password"])
    services_field = builder.get_object("services_field")
    services_field.set_text(__options["services_path"])
    user_bouquet_field = builder.get_object("user_bouquet_field")
    user_bouquet_field.set_text(__options["user_bouquet_path"])
    satellites_xml_field = builder.get_object("satellites_xml_field")
    satellites_xml_field.set_text(__options["satellites_xml_path"])
    data_dir_field = builder.get_object("data_dir_field")
    data_dir_field.set_text(__options["data_dir_path"])

    if dialog.run() == Gtk.ResponseType.OK:
        __options["host"] = host_field.get_text()
        __options["port"] = port_field.get_text()
        __options["user"] = login_field.get_text()
        __options["password"] = password_field.get_text()
        __options["services_path"] = services_field.get_text()
        __options["user_bouquet_path"] = user_bouquet_field.get_text()
        __options["satellites_xml_path"] = satellites_xml_field.get_text()
        __options["data_dir_path"] = data_dir_field.get_text()
        write_config(__options)
    dialog.destroy()


def on_tree_view_key_release(widget, event):
    key = event.keyval
    if key == Gdk.KEY_Tab:
        print("Tab")
    if key == Gdk.KEY_Delete:
        print("Delete")
        on_delete(widget)
    if key == Gdk.KEY_Up:
        print("Up")
    if key == Gdk.KEY_Down:
        print("Down")


def on_upload(item):
    connect(__options, False)


def on_download(item):
    connect(__options)


def on_reload(item):
    pass


def connect(properties, download=True):
    assert isinstance(properties, dict)
    try:
        with FTP(properties["host"]) as ftp:
            ftp.login(user=properties["user"], passwd=properties["password"])
            save_path = properties["data_dir_path"]
            if download:
                # bouquets section
                ftp.cwd(properties["services_path"])
                files = []
                ftp.dir(files.append)
                for file in files:
                    name = str(file).strip()
                    if name.endswith(__DATA_FILES_LIST):
                        name = name.split()[-1]
                        with open(save_path + name, 'wb') as f:
                            ftp.retrbinary('RETR ' + name, f.write)
                # satellites.xml section
                ftp.cwd(properties["satellites_xml_path"])
                files.clear()
                ftp.dir(files.append)
                for file in files:
                    name = str(file).strip()
                    xml_file = "satellites.xml"
                    if name.endswith(xml_file):
                        with open(save_path + xml_file, 'wb') as f:
                            ftp.retrbinary('RETR ' + xml_file, f.write)
                __status_bar.push(1, ftp.voidcmd("NOOP"))
                for name in os.listdir(save_path):
                    print(name)
            else:
                for file_name in os.listdir(save_path):
                    print(file_name)
                    # Open the file for transfer in binary mode
                    # f = open(file_name, "rb")
                    # transfer the file into receiver
                    # send = ftp.storbinary("STOR " + file_name, f)
    except Exception as e:
        __status_bar.remove_all(1)
        __status_bar.push(1, getattr(e, "message", repr(e)))  # Or maybe so: getattr(e, 'message', str(e))


def init_ui():
    builder = Gtk.Builder()
    builder.add_from_file("editor_ui.glade")
    main_window = builder.get_object("main_window")
    global __services_view
    __services_view = builder.get_object("services_tree_view")
    global __fav_view
    __fav_view = builder.get_object("fav_tree_view")
    global __bouquets_view
    __bouquets_view = builder.get_object("bouquets_tree_view")
    # global __services_model
    # __services_model = builder.get_object("services_list_store")
    # global __bouquets_model
    # __bouquets_model = builder.get_object("bouquets_tree_store")
    global __fav_model
    __fav_model = builder.get_object("fav_list_store")
    global __status_bar
    __status_bar = builder.get_object("status_bar")
    builder.connect_signals(get_handlers())
    main_window.show_all()


def start_app():
    init_ui()
    Gtk.main()


def close_app():
    Gtk.main_quit()


if __name__ == "__main__":
    start_app()
