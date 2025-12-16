from zipfile import ZipFile

from prdl.prdl import PrDlCrawl, PrDlPodcast


class TestDefaultCrawler:
    def test_attachments(self):
        # Given
        with open("./tests/data/attachments.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) == 1
        assert (
            result[0].file_name
            == "konstytucja-3-maja-czy-mogla-uratowac-i-rzeczpospolita-historie-jak-z-ksiazki-trojka.mp3"
        )

    def test_audiobook(self):
        """ https://www.polskieradio.pl/podcast/ziemia-obiecana-wladyslaw-stanislaw-reymont,594 """
        # Given
        with open("./tests/data/audiobook_full.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_podcasts_episodes_escaped(self):
        # Given
        with open("./tests/data/podcasts_episodes_escaped.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_podcasts_escaped(self):
        # Given
        with open("./tests/data/podcasts_escaped.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0
        assert type(result) is list
        assert type(result[0]) is PrDlPodcast
        assert result[0].uid == 653
        assert result[3].title == "Mroczna historia Watykanu"
        assert result[3].file_name == "mroczna-historia-watykanu.mp3"
        assert len(result) == 10

    def test_jedynka(self):
        """url: https://jedynka.polskieradio.pl/artykul/810503,Weterani-powstania-czyli-oczko-w-g%C5%82owie-Pi%C5%82sudskiego-"""
        # Given
        with open("./tests/data/jedynka.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_polskieradio24(self):
        """url: https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie"""
        # Given
        with open("./tests/data/polskieradio24.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_data_media(
            given_page_data,
            "https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie",
        )
        # Then
        assert len(result) == 1
        assert result[0].url == "https://static.prsa.pl/351fd590-234a-4364-8061-38546a26df45.mp3"
