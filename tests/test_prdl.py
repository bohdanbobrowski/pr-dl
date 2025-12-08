from prdl.prdl import PrDlCrawl


class TestDefaultCrawler:
    # def test_prdl_get_podcasts_v2(self):
    #     # Given
    #     with open("./tests/data/page1.html", "r") as f:
    #         given_page_data = f.read()
    #     # When
    #     result = PrDlCrawl.get_podcasts_v2(given_page_data)
    #     # Then
    #     assert result is not None
    #     assert type(result) is list
    #     assert type(result[0]) is dict
    #     assert result[0]["id"] == 653
    #     assert result[3]["title"] == "Mroczna historia Watykanu"
    #     assert result[3]["language"] == "pl"
    #     assert len(result) == 10

    def test_prdl_get_podcasts_v2_page3(self):
        # Given
        with open("./tests/data/page2.html", "r") as f:
            given_page_data = f.read()
        # When
        result = PrDlCrawl.get_podcasts_v2(given_page_data)
        # Then
        assert result is not None

