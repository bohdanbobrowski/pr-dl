#!/usr/bin/env python3
# -*- coding : utf-8 -*-
# Author: Bohdan Bobrowski

from setuptools import setup

setup(
    name='pr-dl',
    version='0.1',
    description="Polish Radio Downloader",
    url="https://github.com/bohdanbobrowski/prdl",
    author="Bohdan Bobrowski",
    author_email="bohdanbobrowski@gmail.com",
    license="MIT",
    packages=["prdl"],
    install_requires=["eyed3", "mutagen", "slugify", "pycurl", "pillow", "clint"],
    entry_points={
        'console_scripts': [
            'prdl = prdl.prdlcli:main'
        ],
    },
)
