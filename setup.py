# -*- coding: utf-8 -*-

"""
To upload to PyPI, PyPI test, or a local server:
python setup.py bdist_wheel upload -r <server_identifier>
"""

import setuptools

setuptools.setup(
    name='matrix_vision_camera',
    version='0.1.0',
    author='Andreas Mittelberger',
    author_email='Brow71189@gmail.com',
    description='Use Matrix Vision camera with Nion Swift.',
    packages=['nionswift_plugin.mv_camera', 'mv_utils'],
    install_requires=['nionswift-instrumentation', 'matrix_vision_image_acquisition'],
    requires=['matrix_vision_image_acquisition'],
    license='LGPLv3',
    include_package_data=True,
    python_requires='~=3.5',
    zip_safe=False
)
