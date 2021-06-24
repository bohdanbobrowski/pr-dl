#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

setup(
    name='pr-dl',
    version='0.8.1',
    description="Polish Radio Downloader",
    url="https://github.com/bohdanbobrowski/pr-dl",
    author="Bohdan Bobrowski",
    author_email="bohdanbobrowski@gmail.com",
    license="MIT",
    packages=[
        "prdl"
    ],
    install_requires=[
        "lxml",
        "eyed3",
        "mutagen",
        "python-slugify",
        "pycurl",
        "pillow",
        "clint",
        "download",
        "validators"
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
