PR-DL: Polskie Radio DownLoader
==

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).
Skrypt powstawał przez lata. Był pisany lewą nogą, bez planu i wymagałby srogiego refaktoru.
W zasadzie jedyną jego zaletą jest to, że jako-tako działa(ł)*.

* własnie nie działa zupełnie, i może bym go naprawił?

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
