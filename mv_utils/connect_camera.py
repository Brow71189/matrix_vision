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