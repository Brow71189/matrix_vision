# system imports
import gettext
import numpy as np
import time
import copy
from nion.swift.model import DataItem
from nion.swift.model import DocumentModel

# local libraries
from nion.typeshed import API_1_0 as API

_ = gettext.gettext


class AverageIntensityMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("Measure Average Intensity")  # menu item name
    def __init__(self):
        self.event_listeners = dict()

    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
            target_data_item = window.target_data_item
            if target_data_item is not None and target_data_item.display_xdata.is_datum_2d:
                rect = target_data_item.add_rectangle_region(0.5, 0.5, 0.33, 0.33)
                def update_rect_label(prop):
                    if prop == 'bounds':
                        mask = rect._graphic.get_mask(target_data_item.display_xdata.data.shape)
                        average = np.atleast_1d(np.sum(target_data_item.display_xdata.data*mask, axis=(0,1), dtype=np.float)/
                                                np.count_nonzero(mask, axis=(0,1)))
                        label_string = 'Average intensity: '
                        if target_data_item.display_xdata.is_data_rgb:
                            label_string += '(R: {:g}, G: {:g}, B: {:g})'
                            average = average[..., ::-1]
                        else:
                            label_string += '{:g}'

                        rect.label = label_string.format(*average)
                timestamp = str(time.time())
                self.event_listeners[timestamp] = [rect._graphic.property_changed_event.listen(update_rect_label)]
                self.event_listeners[timestamp].append(rect._graphic.about_to_be_removed_event.listen(lambda: self.event_listeners.pop(timestamp, 0)))
                self.event_listeners[timestamp].append(target_data_item._data_item.data_changed_event.listen(lambda: update_rect_label('bounds')))
                update_rect_label('bounds')
        except Exception as e:
            print(e)

split_channels_script = """
import copy
channel_remove = [(1, 2), (0, 2), (0, 1)]
xdata = copy.deepcopy(src.display_xdata)
xdata.data[..., channel_remove[channel]] = 0
target.xdata = xdata
target.set_dimensional_calibrations(src.display_xdata.dimensional_calibrations)
target.set_intensity_calibration(src.display_xdata.intensity_calibration)
"""

processing_descriptions = lambda channel: {
    "univie.extension.split_channels" + ['_b', '_g', '_r'][channel]:
        {'script': split_channels_script,
         'sources': [
                     {'name': 'src', 'label': 'Source', 'requirements': [{'type': 'rgb'}]}
                     ],
         'parameters': [
                        {'name': 'channel', 'label': 'Channel', 'type': 'integral', 'value': channel, 'value_default': channel, 'value_min': 0, 'value_max': 2, 'control_type': 'slider'}
                        ],
         'title': ['Blue', 'Green', 'Red'][channel] + ' Channel'
         }
}

class SplitChannelsMenuItem:

    menu_id = "_processing_menu"  # required, specify menu_id where this item will go
    menu_item_name = _("Split Channels")  # menu item name

    for channel in range(3):
        DocumentModel.DocumentModel.register_processing_descriptions(processing_descriptions(channel))


    def menu_item_execute(self, window: API.DocumentWindow) -> None:
        try:
#            target_data_item = window.target_data_item
#            if target_data_item is not None and target_data_item.display_xdata.is_data_rgb:
#                channel_names = ['Blue', 'Green', 'Red']
#                channel_remove = [(1,2), (0,2), (0,1)]
#                for i in range(3):
#                    xdata = copy.deepcopy(target_data_item.xdata)
#                    xdata.data[..., channel_remove[i]] = 0
#                    window.create_data_item_from_data_and_metadata(xdata, title=channel_names[i] + ' channel of ' + target_data_item.title)
            document_controller = window._document_controller
            display_specifier = document_controller.selected_display_specifier

            if display_specifier.data_item and display_specifier.data_item.xdata.is_data_rgb:
                for channel in range(3):
                    data_item = document_controller.document_model.make_data_item_with_computation("univie.extension.split_channels" + ['_b', '_g', '_r'][channel], [(display_specifier.data_item, None)])
                    new_display_specifier = DataItem.DisplaySpecifier.from_data_item(data_item)
                    document_controller.display_data_item(new_display_specifier)
        except Exception as e:
            print(e)


class SplitChannelsExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.split_channels"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(SplitChannelsMenuItem())

    def close(self):
        self.__menu_item_ref.close()

class AverageIntensityExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.average_intensity"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(AverageIntensityMenuItem())

    def close(self):
        self.__menu_item_ref.close()