#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

setup(
    name='pr-dl',
    version='0.4',
    description="Polish Radio Downloader",
    url="https://github.com/bohdanbobrowski/pr-dl",
    author="Bohdan Bobrowski",
    author_email="bohdanbobrowski@gmail.com",
    license="MIT",
    packages=[
        "prdl"
    ],
    install_requires=[
        "eyed3==0.8.12",
        "mutagen",
        "slugify",
        "pycurl",
        "pillow",
        "clint",
        "download"
    ],
    entry_points={
        'console_scripts': [
            'prdl = prdl.prdlcli:main'
        ],
    },
    package_data={
        'prdl': [
            '*.jpg'
        ]
    },
    include_package_data = True,
)
