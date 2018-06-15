# system imports
import gettext
import numpy as np
import time

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
                update_rect_label('bounds')
        except Exception as e:
            print(e)


class AnalysisToolsExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.analysis_tools"

    def __init__(self, api_broker):
        # grab the api object.
        api = api_broker.get_api(version="1", ui_version="1")
        # be sure to keep a reference or it will be closed immediately.
        self.__menu_item_ref = api.create_menu_item(AverageIntensityMenuItem())

    def close(self):
        self.__menu_item_ref.close()