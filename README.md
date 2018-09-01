PR-DL: Polskie Radio DownLoader
==

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).

Instalacja:
====

Jak użyć:
====

    prdl [url] [-t] [-f]

W miejsce parametru url wklejamy link do strony w serwisie Polskiego Radia, lub słowo lub frazę jaką chcemy wyszukać.

Opcjonalny parametr -t pozwala zaakceptować wszystkie pliki z góry.

Przykład:
====

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

- po dość głębokim refactorze nie wszystko jeszcze działa jak powinno,
- podcasty się ściągają, ale np. skrypt znajduje tylko pierwszy, zamiast kilku które są na stronie,
- nie uwzględniana jest paginacja,
- coś jest nie halo z zapisem miniatur.

Plany:
====

Będę starał się skrypt utrzymywać i rozwijać, gdyż sam z niego regularnie korzystam.

Mimo pewnych (ekhm...) zmian w Polskim Radiu, nadal pojawia się tam sporo wartościowego contentu... który wystarczy tylko odpowiednio odsiać... ;-) 