from prdl.prdl import PrDlCrawl, PrDlPodcast


class TestDefaultCrawler:
    def test_one(self):
        # Given
        with open("./tests/data/page6.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        pass
        assert len(result) > 0

    def test_prdl_get_podcasts_v2(self):
        # Given
        with open("./tests/data/page1.html") as f:
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

    def test_prdl_get_podcasts_v2_page2(self):
        # Given
        with open("./tests/data/page2.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_prdl_get_podcasts_v2_page3(self):
        # Given
        with open("./tests/data/page3.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_prdl_get_podcasts_v2_jedynka(self):
        """url: https://jedynka.polskieradio.pl/artykul/810503,Weterani-powstania-czyli-oczko-w-g%C5%82owie-Pi%C5%82sudskiego-"""
        # Given
        with open("./tests/data/page4.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_prdl_get_podcasts_data_media(self):
        """url: https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie"""
        # Given
        with open("./tests/data/page5.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl._get_podcasts_data_media(
            given_page_data,
            "https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie",
        )
        # Then
        assert len(result) == 1
