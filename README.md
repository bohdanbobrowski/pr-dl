pr-dl
=====

Proste pobieranie podkastów z serwisu internetowego Polskiego Radia (polskieradio.pl).

Jak użyć:
====

python pr-dl-cli.pl [url] [-t]

W miejsce parametru url wklejamy link do strony w serwisie Polskiego Radia, lub słowo lub frazę jaką chcemy wyszukać.

Opcjonalny parametr -t pozwala zaakceptować wszystkie pliki z góry.

Przykład:
====

Aby pobrać wszystkie podkasty z pierwszej strony "Klubu Ludzi Ciekawych Wszystkiego" wpisujemy:
python pr-dl-cli.py http://www.polskieradio.pl/8/Audycja/7298 -t

"Klub Trójki" pobieramy tak:
python pr-dl-cli.py http://www.polskieradio.pl/9/Audycja/7422 -t

Aby wyszukać słowo lub frazę skrypt odpalamy tak:
python pr-dl-cli.py Wańkowicz -t

lub:
python pr-dl-cli.py Sergiusz\ Piasecki -t

Niedoskonałości:
====

Niestety skrypt nie ogarnia "paginacji", która na stronach Polskiego Radia rozwiązana jest w taki ajaksowy, fikuśny sposób. Pobierane są zatem tylko podkasty z pierwszej strony.
