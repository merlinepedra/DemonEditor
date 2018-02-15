from app.commons import run_idle
from app.eparser import Service
from app.ui.main_helper import get_base_model, is_only_one_item_selected
from . import Gtk, UI_RESOURCES_PATH


class ServiceDetailsDialog:
    def __init__(self, transient, options, view):
        builder = Gtk.Builder()
        builder.add_from_file(UI_RESOURCES_PATH + "service_details_dialog.glade")

        self._dialog = builder.get_object("service_details_dialog")
        self._dialog.set_transient_for(transient)
        self._options = options
        self._services_view = view
        # Service elements
        self._name_entry = builder.get_object("name_entry")
        self._package_entry = builder.get_object("package_entry")
        self._id_entry = builder.get_object("id_entry")
        self._type_entry = builder.get_object("type_entry")
        self._extra_entry = builder.get_object("extra_entry")
        self._bitstream_entry = builder.get_object("bitstream_entry")
        self._pcm_entry = builder.get_object("pcm_entry")
        self._reference_entry = builder.get_object("reference_entry")
        self._video_pid_entry = builder.get_object("video_pid_entry")
        self._pcr_pid_entry = builder.get_object("pcr_pid_entry")
        self._mpeg_pid_entry = builder.get_object("mpeg_pid_entry")
        self._ac3_pid_entry = builder.get_object("ac3_pid_entry")
        self._ac3plus_pid_entry = builder.get_object("ac3plus_pid_entry")
        self._acc_pid_entry = builder.get_object("acc_pid_entry")
        self._he_acc_pid_entry = builder.get_object("he_acc_pid_entry")
        self._teletext_pid_entry = builder.get_object("teletext_pid_entry")
        self._keep_check_button = builder.get_object("keep_check_button")
        self._hide_check_button = builder.get_object("hide_check_button")
        self._use_pids_check_button = builder.get_object("use_pids_check_button")
        self._new_check_button = builder.get_object("new_check_button")
        # Transponder elements
        self._sat_pos_combo_box = builder.get_object("sat_pos_combo_box")
        self._transponder_id_entry = builder.get_object("transponder_id_entry")
        self._network_id_entry = builder.get_object("network_id_entry")
        self._freq_entry = builder.get_object("freq_entry")
        self._rate_entry = builder.get_object("rate_entry")
        self._pol_combo_box = builder.get_object("pol_combo_box")
        self._fec_combo_box = builder.get_object("fec_combo_box")
        self._sys_combo_box = builder.get_object("sys_combo_box")
        self._mod_combo_box = builder.get_object("mod_combo_box")
        self._invertion_combo_box = builder.get_object("invertion_combo_box")
        self._rolloff_combo_box = builder.get_object("rolloff_combo_box")
        self._pilot_combo_box = builder.get_object("pilot_combo_box")
        self._pls_mode_combo_box = builder.get_object("pls_mode_combo_box")
        self._pls_code_entry = builder.get_object("pls_code_entry")
        self._stream_id_entry = builder.get_object("stream_id_entry")
        self._flags_entry = builder.get_object("flags_entry")
        self._namespace_entry = builder.get_object("namespace_entry")
        self.update_data_elements()

    @run_idle
    def update_data_elements(self):
        model, paths = self._services_view.get_selection().get_selected_rows()
        model = get_base_model(model)
        if is_only_one_item_selected(paths, self._dialog):
            srv = Service(*model[paths][:])
            self._name_entry.set_text(srv.service)
            self._package_entry.set_text(srv.package)
            self._type_entry.set_text("")
            self._id_entry.set_text(str(int(srv.ssid, 16)))
            self._reference_entry.set_text(srv.picon_id.replace("_", ":").rstrip(".png"))
            # transponder
            self._freq_entry.set_text(srv.freq)
            self._rate_entry.set_text(srv.rate)
            self.select_active_text(self._pol_combo_box, srv.pol)
            self.select_active_text(self._fec_combo_box, srv.fec)
            self.select_active_text(self._sys_combo_box, srv.system)

    def select_active_text(self, box: Gtk.ComboBox, text):
        model = box.get_model()
        for index, row in enumerate(model):
            if row[0] == text:
                box.set_active(index)
                break

    def show(self):
        response = self._dialog.run()
        if response == Gtk.ResponseType.OK:
            pass
        self._dialog.destroy()

        return response


if __name__ == "__main__":
    dialog = ServiceDetailsDialog()
    dialog.show()