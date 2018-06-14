#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 10:23:33 2018

@author: mittelberger2
"""

import mv

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
    