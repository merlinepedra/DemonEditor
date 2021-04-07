import os
from enum import Enum, IntEnum
from functools import lru_cache

from app.settings import Settings, SettingsException, IS_WIN, SEP

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Setting mod mask for keyboard depending on platform
MOD_MASK = Gdk.ModifierType.CONTROL_MASK
# Path to *.glade files
UI_PATH = "app{}ui{}".format(SEP, SEP)
UI_RESOURCES_PATH = UI_PATH if os.path.exists(UI_PATH) else "ui{}".format(SEP)
LANG_PATH = UI_RESOURCES_PATH + "lang"
GTK_PATH = os.environ.get("GTK_PATH", None)
NOTIFY_IS_INIT = False
IS_GNOME_SESSION = int(bool(os.environ.get("GNOME_DESKTOP_SESSION_ID")))
# Translation.
TEXT_DOMAIN = "demon-editor"
APP_FONT = None

try:
    settings = Settings.get_instance()
except SettingsException:
    pass
else:
    os.environ["LANGUAGE"] = settings.language

    st = Gtk.Settings().get_default()
    APP_FONT = st.get_property("gtk-font-name")
    st.set_property("gtk-application-prefer-dark-theme", settings.dark_mode)

    if settings.is_themes_support:
        st.set_property("gtk-theme-name", settings.theme)
        st.set_property("gtk-icon-theme-name", settings.icon_theme)

theme = Gtk.IconTheme.get_default()
theme.append_search_path(GTK_PATH + "{}share{}icons".format(SEP, SEP) if GTK_PATH else UI_RESOURCES_PATH + "icons")


def get_theme_icon(icon_theme, name, size):
    try:
        return icon_theme.load_icon(name, size, 0)
    except GLib.Error:
        pass


_IMAGE_MISSING = get_theme_icon(theme, "image-missing", 16)
CODED_ICON = get_theme_icon(theme, "emblem-readonly", 16) or _IMAGE_MISSING
LOCKED_ICON = get_theme_icon(theme, "changes-prevent-symbolic", 16) or _IMAGE_MISSING
HIDE_ICON = get_theme_icon(theme, "go-jump", 16) or _IMAGE_MISSING
TV_ICON = get_theme_icon(theme, "tv-symbolic", 16) or _IMAGE_MISSING
IPTV_ICON = get_theme_icon(theme, "emblem-shared", 16)
EPG_ICON = get_theme_icon(theme, "gtk-index", 16)
DEFAULT_ICON = get_theme_icon(theme, "emblem-default", 16)


@lru_cache(maxsize=1)
def get_yt_icon(icon_name, size=24):
    """ Getting  YouTube icon.

        If the icon is not found in the icon themes, the "Info" icon is returned by default!
    """
    default_theme = Gtk.IconTheme.get_default()
    if default_theme.has_icon(icon_name):
        return default_theme.load_icon(icon_name, size, 0)

    n_theme = Gtk.IconTheme.new()
    p_path = "{}usr{}share{}icons{}*".format(SEP, SEP, SEP, SEP)

    import glob

    for theme_name in map(os.path.basename, filter(os.path.isdir, glob.glob(p_path))):
        theme.set_custom_theme(theme_name)
        if n_theme.has_icon(icon_name):
            return n_theme.load_icon(icon_name, size, 0)

    if default_theme.lookup_icon(Gtk.STOCK_APPLY, size, 0):
        return default_theme.load_icon(Gtk.STOCK_APPLY, size, 0)


def show_notification(message, timeout=10000, urgency=1):
    """ Shows notification.

        @param message: text to display
        @param timeout: milliseconds
        @param urgency: 0 - low, 1 - normal, 2 - critical
    """
    pass


class KeyboardKey(Enum):
    """ The raw(hardware) codes of the keyboard keys. """
    E = 69 if IS_WIN else 26
    R = 82 if IS_WIN else 27
    T = 84 if IS_WIN else 28
    P = 80 if IS_WIN else 33
    S = 83 if IS_WIN else 39
    F = 70 if IS_WIN else 41
    X = 88 if IS_WIN else 53
    C = 67 if IS_WIN else 54
    V = 86 if IS_WIN else 55
    W = 87 if IS_WIN else 25
    Z = 90 if IS_WIN else 52
    INSERT = 45 if IS_WIN else 118
    HOME = 36 if IS_WIN else 110
    END = 35 if IS_WIN else 115
    UP = 38 if IS_WIN else 111
    DOWN = 40 if IS_WIN else 116
    PAGE_UP = 33 if IS_WIN else 112
    PAGE_DOWN = 34 if IS_WIN else 117
    LEFT = 37 if IS_WIN else 113
    RIGHT = 39 if IS_WIN else 114
    F2 = 113 if IS_WIN else 68
    F7 = 118 if IS_WIN else 73
    SPACE = 32 if IS_WIN else 65
    DELETE = 46 if IS_WIN else 119
    BACK_SPACE = 8 if IS_WIN else 22
    CTRL_L = 17 if IS_WIN else 37
    CTRL_R = 163 if IS_WIN else 105
    # Laptop codes
    HOME_KP = 79
    END_KP = 87
    PAGE_UP_KP = 81
    PAGE_DOWN_KP = 89

    @classmethod
    def value_exist(cls, value):
        return value in (val.value for val in cls.__members__.values())


# Keys for move in lists. KEY_KP_(NAME) for laptop!!!
MOVE_KEYS = (KeyboardKey.UP, KeyboardKey.PAGE_UP, KeyboardKey.DOWN, KeyboardKey.PAGE_DOWN, KeyboardKey.HOME,
             KeyboardKey.END, KeyboardKey.HOME_KP, KeyboardKey.END_KP, KeyboardKey.PAGE_UP_KP, KeyboardKey.PAGE_DOWN_KP)


class FavClickMode(IntEnum):
    """ Double click mode on the service in the bouquet(FAV) list. """
    DISABLED = 0
    STREAM = 1
    PLAY = 2
    ZAP = 3
    ZAP_PLAY = 4


class ViewTarget(Enum):
    """ Used for set target view. """
    BOUQUET = 0
    FAV = 1
    SERVICES = 2


class BqGenType(Enum):
    """  Bouquet generation type. """
    SAT = 0
    EACH_SAT = 1
    PACKAGE = 2
    EACH_PACKAGE = 3
    TYPE = 4
    EACH_TYPE = 5


class Column(IntEnum):
    """ Column nums in the views """
    # Main view
    SRV_CAS_FLAGS = 0
    SRV_STANDARD = 1
    SRV_CODED = 2
    SRV_SERVICE = 3
    SRV_LOCKED = 4
    SRV_HIDE = 5
    SRV_PACKAGE = 6
    SRV_TYPE = 7
    SRV_PICON = 8
    SRV_PICON_ID = 9
    SRV_SSID = 10
    SRV_FREQ = 11
    SRV_RATE = 12
    SRV_POL = 13
    SRV_FEC = 14
    SRV_SYSTEM = 15
    SRV_POS = 16
    SRV_DATA_ID = 17
    SRV_FAV_ID = 18
    SRV_TRANSPONDER = 19
    SRV_TOOLTIP = 20
    SRV_BACKGROUND = 21
    # FAV view
    FAV_NUM = 0
    FAV_CODED = 1
    FAV_SERVICE = 2
    FAV_LOCKED = 3
    FAV_HIDE = 4
    FAV_TYPE = 5
    FAV_POS = 6
    FAV_ID = 7
    FAV_PICON = 8
    FAV_TOOLTIP = 9
    FAV_BACKGROUND = 10
    # Bouquets view
    BQ_NAME = 0
    BQ_LOCKED = 1
    BQ_HIDDEN = 2
    BQ_TYPE = 3
    # Alternatives view
    ALT_NUM = 0
    ALT_PICON = 1
    ALT_SERVICE = 2
    ALT_TYPE = 3
    ALT_POS = 4
    ALT_FAV_ID = 5
    ALT_ID = 6
    ALT_ITER = 7

    def __index__(self):
        """ Overridden to get the index in slices directly """
        return self.value


if __name__ == "__main__":
    pass
