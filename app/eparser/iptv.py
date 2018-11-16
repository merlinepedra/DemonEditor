""" Module for IPTV and streams support """
from enum import Enum

from app.properties import Profile
from app.ui.uicommons import IPTV_ICON
from .ecommons import BqServiceType, Service

# url, description, urlkey, account, usrname, psw, s_type, iconsrc, iconsrc_b, group
NEUTRINO_FAV_ID_FORMAT = "{}::{}::{}::{}::{}::{}::{}::{}::{}::{}"
ENIGMA2_FAV_ID_FORMAT = " {}:0:{}:{:X}:{:X}:{:X}:{:X}:0:0:0:{}:{}\n#DESCRIPTION: {}\n"


class StreamType(Enum):
    DVB_TS = "1"
    NONE_TS = "4097"


def parse_m3u(path, profile):
    with open(path) as file:
        aggr = [None] * 10
        channels = []
        name = None
        fav_id = None
        for line in file.readlines():
            if line.startswith("#EXTINF"):
                name = line[1 + line.index(","):].strip()
            elif not line.startswith("#"):
                if profile is Profile.ENIGMA_2:
                    fav_id = ENIGMA2_FAV_ID_FORMAT.format(StreamType.NONE_TS.value, 1, 0, 0, 0, 0,
                                                          line.strip().replace(":", "%3a"), name, name, None)
                elif profile is Profile.NEUTRINO_MP:
                    fav_id = NEUTRINO_FAV_ID_FORMAT.format(line.strip(), "", 0, None, None, None, None, "", "", 1)
                srv = Service(None, None, IPTV_ICON, name, *aggr[0:3], BqServiceType.IPTV.name, *aggr, fav_id, None)
                channels.append(srv)

    return channels


if __name__ == "__main__":
    pass
