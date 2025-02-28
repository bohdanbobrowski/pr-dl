PR-DL: Polskie Radio DownLoader
==

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).

Skrypt powstawał przez lata. Był pisany lewą nogą i wymagałby srogiego refaktoru. Jak widzę niektóre jego elementy to się za głowę łapię! W zasadzie jedyną jego zaletą jest to, że jako-tako działa.

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

Versions history:
====

- 0.9 - pracuję nad tym, cierpliwości
- 0.8.2 - przywrócenie domyślnej miniaturki
- 0.8.1 - odpowiedź na zgłoszone błędy: https://github.com/bohdanbobrowski/pr-dl/issues/3
- 0.8 - drobny refactor, poprawione pobieranie
- 0.7 - szukanie działa znowu!
- 0.6 - przejście na python3
- 0.5
