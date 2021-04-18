PR-DL: Polskie Radio DownLoader
==

Documentation is only in polish here - beacause Polish Radio is in polish :-)

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).

Skrypt powstawał przez lata. Był pisany lewą nogą i wymagałby srogiego refaktoru. Jak widzę niektóre jego elementy to się za głowę łapię! W zasadzie jedyną jego zaletą jest to, że jako-tako działa.

Instalacja:
====

    pip install git+https://github.com/bohdanbobrowski/pr-dl

Jak użyć:
====

    prdl [url] [-t] [-f]

W miejsce parametru url wklejamy link do strony w serwisie Polskiego Radia, lub słowo lub frazę jaką chcemy wyszukać.

Opcjonalny parametr -t pozwala zaakceptować wszystkie pliki z góry.

Przykład:
====

Aby pobrać wskazaną audycję należy wykonac komendę np.:

    prdl https://www.polskieradio.pl/8/755/Artykul/426557


Aby wyszukać słowo lub frazę w wyszukiwarce Polskiego Radia skrypt odpalamy tak:
    
    prdl Wańkowicz

lub z -f na końcu dla "wzmocnionego" szukania w tytułach (wyszukiwarka PR niestety wyrzuca całą masę chłamu):
    
    prdl "Sergiusz Piasecki" -f

parametr -t powoduje że wszystkie podcasty zostaną pobrane bez pytania o zgodę:

Plany:
====

Będę starał się skrypt utrzymywać i rozwijać, gdyż sam z niego regularnie korzystam.

Mimo pewnych (nie koniecznie) zmian w Polskim Radiu, nadal pojawia się tam sporo wartościowego contentu... który wystarczy tylko odpowiednio odsiać... ;-)

Historia wersji:
====

- 0.5
- 0.6 - przejście na python3
- 0.7 - szukanie działa znowu!
- 0.8 - drobny refactor, poprawione pobieranie