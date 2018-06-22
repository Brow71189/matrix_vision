# standard libraries
import gettext
import threading
import typing

# third party libraries

# local libraries
from nion.ui import Declarative
from nion.utils import Model
from nion.utils import Registry
from nion.utils import Event

from mv_utils import mv_acquisition_thread, connect_camera

_ = gettext.gettext

class VideoCamera:

    def __init__(self, camera_index):
        self.camera_index = camera_index
        self.device = connect_camera.get_camera_with_index(camera_index)['camera']
        self.periodic_event = Event.Event()
        connect_camera.apply_config_file_settings(self.device)
        self.spatial_calibrations = [{},{}]

    def update_settings(self, settings: dict) -> None:
        camera_index = settings.get("camera_index", 0)
        if camera_index != self.camera_index:
            self.device = connect_camera.get_camera_with_index(camera_index)['camera']
            self.camera_index = camera_index

    def start_acquisition(self):
        #video_capture = cv2.VideoCapture(self.__source)
        self.buffer_ref = [None]
        self.cancel_event = threading.Event()
        self.ready_event = threading.Event()
        self.done_event = threading.Event()
        self.thread = mv_acquisition_thread.AcquisitionThread(self.device, self.buffer_ref, self.cancel_event,
                                                              self.ready_event, self.done_event)
        self.thread.periodic_event = self.periodic_event
        #self.thread = threading.Thread(target=video_capture_thread, args=(video_capture, self.buffer_ref, self.cancel_event, self.ready_event, self.done_event))
        self.thread.start()

    def acquire_data(self):
        self.ready_event.wait()
        self.ready_event.clear()
        data = self.buffer_ref[0]['img']
        data_element = {
                    'data': data,
                    'spatial_calibrations': self.spatial_calibrations
                }
        #print(self.device.Setting.Base.GenICam.AcquisitionControl.mvAcquisitionMemoryFrameCount, end='\r')
        self.done_event.set()
        return data_element

    def stop_acquisition(self):
        self.cancel_event.set()
        self.done_event.set()
        self.thread.join()


class VideoDeviceFactory:

    display_name = _("Matrix Vision")
    factory_id = "univie.mv_factory"

    def __init__(self):
        self.available_cameras = connect_camera.list_devices()

    def make_video_device(self, settings: dict) -> typing.Optional[VideoCamera]:
        if settings.get("driver") == self.factory_id:
            camera_index = settings.get("camera_index", 0)
            video_device = VideoCamera(camera_index)
            video_device.camera_id = settings.get("device_id")
            video_device.camera_name = settings.get("name")
            video_device.driver_id = self.factory_id
            return video_device
        return None

    def describe_settings(self) -> typing.List[typing.Dict]:
        return [
                {'name': 'camera_index', 'type': 'int'}
                ]

    def get_editor_description(self):
        u = Declarative.DeclarativeUI()

        camera_names = [cam.get('product', cam.get('serial')) for cam in self.available_cameras]
        camera_index_combo = u.create_combo_box(items=camera_names, current_index="@binding(camera_index_model.value)")

        label_column = u.create_column(u.create_label(text=_("Select camera from list:")), spacing=4)
        field_column = u.create_column(camera_index_combo, spacing=4)

        return u.create_row(label_column, field_column, u.create_stretch(), spacing=12)

    def create_editor_handler(self, settings):
        available_cameras = self.available_cameras
        class EditorHandler:

            def __init__(self, settings):
                self.settings = settings

                self.camera_index_model = Model.PropertyModel()

                def camera_index_changed(index):
                    formats = list(range(len(available_cameras)))
                    self.settings.camera_index = formats[index]

                self.camera_index_model.on_value_changed = camera_index_changed

                self.camera_index_model.value = self.settings.camera_index

        return EditorHandler(settings)


class MVCamExtension:

    # required for Swift to recognize this as an extension class.
    extension_id = "univie.mv_camera"

    def __init__(self, api_broker):
        # grab the api object.
        self.api = api_broker.get_api(version="1", ui_version="1")

    Registry.register_component(VideoDeviceFactory(), {"video_device_factory"})

    def close(self):
        pass
