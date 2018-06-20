class PanelDelegate:
    def __init__(self, api):
        self.__api = api
        self.panel_id = 'matrix-vision-control-panel'
        self.panel_name = 'Matrix Vision Control'
        self.panel_positions = ['left', 'right']
        self.panel_position = 'right'


    def create_panel_widget(self, ui, document_controller):
        def item_text_getter(item):
            return '{:d}x'.format(item)
        column = ui.create_column_widget()

        self.choose_camera_label = ui.create_label_widget(text='Camera: ')
        self.choose_camera_combo = ui.create_combo_box_widget()

        self.exposure_time_label = ui.create_label_widget(text='Exposure ms: ')
        self.exposure_time_line_edit = ui.create_line_edit_widget()
        self.auto_exposure_label = ui.create_label_widget(text='Auto ')
        self.auto_exposure_check_box = ui.create_check_box_widget()

        self.binning_label = ui.create_label_widget(text='Binning: ')
        self.binning_combo = ui.create_combo_box_widget(items=[1, 2, 4, 8], item_text_getter=item_text_getter)

        self.magnification_label = ui.create_label_widget(text='Magnification: ')
        self.magnification_combo = ui.create_combo_box_widget(items=[5, 10, 20, 50, 100], item_text_getter=item_text_getter)

        row1 = ui.create_row_widget()
        row2 = ui.create_row_widget()
        row3 = ui.create_row_widget()
        row4 = ui.create_row_widget()

        row1.add_spacing(5)
        row1.add(self.choose_camera_label)
        row1.add(self.choose_camera_combo)
        row1.add_stretch()
        row1.add_spacing(5)

        row2.add_spacing(5)
        row2.add(self.exposure_time_label)
        row2.add(self.exposure_time_line_edit)
        row2.add_spacing(10)
        row2.add(self.auto_exposure_label)
        row2.add(self.auto_exposure_check_box)
        row2.add_stretch()
        row2.add_spacing(5)

        row3.add_spacing(5)
        row3.add(self.binning_label)
        row3.add(self.binning_combo)
        row3.add_stretch()
        row3.add_spacing(5)

        row4.add_spacing(5)
        row4.add(self.magnification_label)
        row4.add(self.magnification_combo)
        row4.add_stretch()
        row4.add_spacing(5)

        column.add_spacing(5)
        column.add(row1)
        column.add_spacing(5)
        column.add(row2)
        column.add_spacing(5)
        column.add(row3)
        column.add_spacing(5)
        column.add(row4)
        column.add_stretch()
        column.add_spacing(5)

        self.connect_functions()

        return column

    def connect_functions(self):
        def camera_changed(item):
            pass

        def exposure_changed(text):
            pass

        def auto_exposure_changed(check_state):
            pass

        def binning_changed(item):
            pass

        def magnification_changed(item):
            pass



        self.binning_combo.on_current_item_changed = binning_changed


class MVCamControlPanelExtension:
    extension_id = 'univie.matrix_vision.control_panel'

    def __init__(self, api_broker):
        api = api_broker.get_api(version='1', ui_version='1')
        self.__panel_ref = api.create_panel(PanelDelegate(api))

    def close(self):
        self.__panel_ref.close()
        self.__panel_ref = None