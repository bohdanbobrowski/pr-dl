PR-DL: Polskie Radio DownLoader
==

Documentation is only in polish here - beacause Polish Radio is in polish :-)

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).

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

    prdl https://www.polskieradio.pl/10/5566/Artykul/1780232

Niestety przykłady poniżej nie działają poz mianach w API Polskiego Radia:
======

Aby pobrać wszystkie podkasty z pierwszej strony "Klubu Ludzi Ciekawych Wszystkiego" wpisujemy:
    
    prdl https://www.polskieradio.pl/8/Audycja/7298 -t

"Klub Trójki" pobieramy tak:
    
    prdl https://www.polskieradio.pl/9/Audycja/7422 -t

Aby wyszukać słowo lub frazę w wyszukiwarce Polskiego Radia skrypt odpalamy tak:
    
    prdl Wańkowicz

lub z -f na końcu dla szukania w tytułach:
    
    prdl Sergiusz\ Piasecki -f

Znane błędy:
====

- działa jedynie pobieranie 

Plany:
====

Będę starał się skrypt utrzymywać i rozwijać, gdyż sam z niego regularnie korzystam.

Mimo pewnych (ekhm...) zmian w Polskim Radiu, nadal pojawia się tam sporo wartościowego contentu... który wystarczy tylko odpowiednio odsiać... ;-)

Historia wersji:
====

- 0.4
- 0.5 - przejście na python3