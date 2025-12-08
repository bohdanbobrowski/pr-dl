from prdl.prdl import PrDlCrawl, PrDlPodcast


class TestDefaultCrawler:
    def test_prdl_get_podcasts_v2(self):
        # Given
        with open("./tests/data/page1.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl.get_podcasts_v2(given_page_data)
        # Then
        assert result is not None
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
        result = PrDlCrawl.get_podcasts_v2(given_page_data)
        # Then
        assert result is not None

    def test_prdl_get_podcasts_v2_page3(self):
        # Given
        with open("./tests/data/page3.html") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl.get_podcasts_v2(given_page_data)
        # Then
        assert result is not None
