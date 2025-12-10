<p align="center">
<img src="./assets/prdl_logo_web.svg" alt="PR-DL" width="300" />
</p>

# PR-DL: Polskie Radio DownLoader

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/bohdanbobrowski/pr-dl/graphs/commit-activity) [![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/) ![GitHub all releases](https://img.shields.io/github/downloads/bohdanbobrowski/pr-dl/total) ![GitHub release (with filter)](https://img.shields.io/github/v/release/bohdanbobrowski/pr-dl) ![GitHub Release Date - Published_At](https://img.shields.io/github/release-date/bohdanbobrowski/pr-dl)

Simple script that downloads podcasts from Polish Radio webservices.

## Installation:

    pip install git+https://github.com/bohdanbobrowski/pr-dl

### Creating local environment   

First, clone repository:

    git clone https://github.com/bohdanbobrowski/pr-dl.git

Then:

    cd pr-dl
    python -m venv .venv
    source  .venv/bin/activate
    pip install -e .[dev]

## Usage:

    prdl --help
    usage: prdl [-h] [-a] [-d] [-f] [-c] url_or_search
    
    Polish Radio Downloader
    
    positional arguments:
      url_or_search         Url or search phrase.
    
    options:
      -h, --help            show this help message and exit
      -a, --all             Save all podcasts without confirmation.
      -d, --debug           Turn on debug mode.
      -f, --forced          Don't trust PR searchengine - show only results with given keyword.
      -c, --cache           Enable local cache.

## Examples:

Single url:

    prdl https://www.polskieradio.pl/8/755/Artykul/426557

Use `-a` argument to download all podcasts:

    prdl https://www.polskieradio.pl/podcast/ziemia-obiecana-wladyslaw-stanislaw-reymont,594 -a

You can also search using Polskie Radio search engine:

    prdl Wańkowicz

I you add `-f` script fill "force" by searching phrase (case insensitive) in given results: 

    prdl "Sergiusz Piasecki" -f

## Building:

    pyinstaller prdl.spec
