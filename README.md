<img src="./assets/prdl_logo_web.svg" alt="PR-DL" width="300" />

PR-DL: Polskie Radio DownLoader
==

Simple script that downloads podcasts from Polish Radio webservices.

Installation:
====

    pip install git+https://github.com/bohdanbobrowski/pr-dl

Usage:
====

    prdl --help
    usage: prdl [-h] [-a] [-f] url_or_search
    
    Polish Radio Downloader
    
    positional arguments:
      url_or_search  Url or search phrase.
    
    options:
      -h, --help     show this help message and exit
      -a, --all      Save all podcasts without confirmation.
      -f, --forced   Don't trust PR searchengine - show only results with given keyword.

Examples:
====

    prdl https://www.polskieradio.pl/8/755/Artykul/426557 -a

    prdl Wańkowicz

    prdl "Sergiusz Piasecki" -f

Building:
====

    pyinstaller prdl.spec
