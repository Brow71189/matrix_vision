#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 10:23:33 2018

@author: mittelberger2
"""

import mv
import configparser
import os

def list_devices():
    return mv.dmg.get_device_list()

def get_camera_with_index(index):
    dev_list = list_devices()
    assert index < len(dev_list), 'Camera index {:d} is larger than number of available cameras ({:d})'.format(index, len(dev_list))
    dev_dict = dev_list[index]
    dev_dict['camera'] = mv.dmg.get_device(dev_dict['serial'])
    return dev_dict

def apply_default_settings(device):
    device.Setting.Base.ImageDestination.PixelFormat = 10
    device.Setting.Base.ImageProcessing.WhiteBalance = 6
    device.Setting.Base.ImageProcessing.WhiteBalanceCalibration = 0
    device.Setting.Base.ImageDestination.ScalerMode = 1
    device.Setting.Base.ImageDestination.ScalerInterpolationMode = 0

def apply_config_file_settings(device):
    parser = configparser.ConfigParser()
    parser.optionxform = lambda option: option #this is to disable conversion of option names to lowercase
    config_path = os.path.expanduser('~/.config/matrix_vision/config.ini')
    print('Loading Matrix Vision camera configuration from {}'.format(config_path))
    if os.path.isfile(config_path):
        parser.read(config_path)
        sections = parser.sections()
        for section in sections:
            lastsec = device.Setting.Base
            try:
                for splitsec in section.split('.'):
                    lastsec = getattr(lastsec, splitsec)
            except AttributeError:
                print('Settings section {} does not exist for this camera.'.format(section))
            else:
                for option in parser[section].keys():
                    try:
                        setattr(lastsec, option, parser.getint(section, option))
                    except mv.MVError:
                        print('Option {} in section {} does not exist for this camera.'.format(option, section))

def get_sensor_size(device):
    return (2056, 2646)

def set_option(device, option_name, value):
    pass

def get_option(device, option_name):
    value = None
    return value

OPTION_DICT = {
    'WhiteBalance': 'Setting.Base.ImageProcessing.WhiteBalance',
    'WhiteBalanceCalibration': 'Setting.Base.ImageProcessing.WhiteBalanceCalibration',
    'ExposureTime': 'Setting.Base.Camera.GenICam.AcquisitionControl.ExposureTime',
    'ExposureAuto': 'Setting.Base.Camera.GenICam.AcquisitionControl.ExposureAuto',
    'ScalerMode': 'Setting.Base.ImageDestination.ScalerMode',
    'ImageHeight': 'Setting.Base.ImageDestination.ImageHeight',
    'ImageWidth': 'Setting.Base.ImageDestination.ImageWidth',
    'FramesPerSecond': 'Statistics.FramesPerSecond',
    'ImageProcTime_s': 'Statistics.ImageProcTime_s'
    }

class CameraSettings:
    def __init__(self, device):
        self.__camera = device

    def _get_option(self, option_name):
        return get_option(self.__camera)

    def _set_option(self, option_name, value):
        set_option(self.__camera, option_name, value)

    @property
    def exposure_ms(self):
        return self._get_option('ExposureTime')

    @exposure_ms.setter
    def exposure_ms(self, exposure):
        if not self.auto_exposure:
            self._set_option('ExposureTime', exposure)

    @property
    def auto_exposure(self):
        return bool(self._get_option('ExposureAuto'))

    @auto_exposure.setter
    def auto_exposure(self, auto):
        self._set_option('ExposureAuto', int(auto))

    @property
    def binning(self):
        return round(get_sensor_size(self.__camera)[0]/self._get_option('ImageHeight'))

    @binning.setter
    def binning(self, binning):
        if binning > 1:
            self._set_option('ScalerMode', 1)
            sensor_size = get_sensor_size(self.__camera)
            self._set_option('ImageHeight', round(sensor_size[0]/binning))
            self._set_option('ImageWidth', round(sensor_size[1]/binning))
        else:
            self._set_option('ScalerMode', 0)