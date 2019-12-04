from urllib.parse import urlparse
from gi.repository import GLib
from app.connections import HttpRequestType
from app.tools.yt import YouTube
from .uicommons import Gtk, Gdk, UI_RESOURCES_PATH, TEXT_DOMAIN


class LinksTransmitter:

    def __init__(self, http_api, app_window):
        handlers = {"on_popup_menu": self.on_popup_menu,
                    "on_status_icon_activate": self.on_status_icon_activate,
                    "on_query_tooltip": self.on_query_tooltip,
                    "on_drag_data_received": self.on_drag_data_received,
                    "on_exit": self.on_exit}

        self._http_api = http_api
        self._app_window = app_window

        builder = Gtk.Builder()
        builder.set_translation_domain(TEXT_DOMAIN)
        builder.add_from_file(UI_RESOURCES_PATH + "transmitter.glade")
        builder.connect_signals(handlers)

        self._tray = builder.get_object("status_icon")
        self._main_window = builder.get_object("main_window")
        self._url_entry = builder.get_object("url_entry")

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(UI_RESOURCES_PATH + "style.css")
        self._url_entry.get_style_context().add_provider_for_screen(Gdk.Screen.get_default(), style_provider,
                                                                    Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def show(self, show):
        self._tray.set_visible(show)
        if not show:
            self.hide()

    def hide(self):
        self._main_window.hide()

    def on_popup_menu(self, menu, button, time):
        menu.popup(None, None, None, None, button, time)

    def on_status_icon_activate(self, window):
        visible = window.get_visible()
        window.hide() if visible else window.show()
        self._app_window.present() if visible else self._app_window.iconify()

    def on_query_tooltip(self, icon, g, x, y, tooltip: Gtk.Tooltip):
        if self._main_window.get_visible() or not self._url_entry.get_text():
            return False

        tooltip.set_text(self._url_entry.get_text())
        return True

    def on_drag_data_received(self, entry, drag_context, x, y, data, info, time):
        url = data.get_text()
        GLib.idle_add(entry.set_text, url)
        gen = self.activate_url(url)
        GLib.idle_add(lambda: next(gen, False), priority=GLib.PRIORITY_LOW)

    def activate_url(self, url):
        self._url_entry.set_name("GtkEntry")
        result = urlparse(url)

        if result.scheme and result.netloc:
            self._url_entry.set_sensitive(False)
            yt_id = YouTube.get_yt_id(url)
            yield True

            if yt_id:
                self._url_entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_INFO)
                links, title = YouTube.get_yt_link(yt_id)
                yield True
                if links:
                    url = links[sorted(links, key=lambda x: int(x.rstrip("p")), reverse=True)[0]]
                else:
                    self.on_play(links)
                    return
            else:
                self._url_entry.set_icon_from_stock(Gtk.EntryIconPosition.SECONDARY, None)

            self._http_api.send(HttpRequestType.PLAY, url, self.on_play)
            yield True

    def on_play(self, res):
        """ Play callback """
        GLib.idle_add(self._url_entry.set_sensitive, True)
        res = res.get("result", None) if res else res
        self._url_entry.set_name("GtkEntry" if res else "digit-entry")

    def on_exit(self, item=None):
        self.show(False)


if __name__ == "__main__":
    pass