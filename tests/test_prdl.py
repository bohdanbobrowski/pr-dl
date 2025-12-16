from zipfile import ZipFile

from prdl.prdl import PrDlCrawl, PrDlPodcast


def read_compressed_demo_data(file_name: str) -> str:
    file_data = b""
    with ZipFile(f"./tests/data/{file_name}.zip") as zf:
        for file in zf.namelist():
            if not file == f"{file_name}.html":  # optional filtering by filetype
                continue
            with zf.open(file) as f:
                file_data = f.read()
    return file_data.decode()


class TestDefaultCrawler:
    def test_attachments(self):
        # Given
        given_page_data = read_compressed_demo_data("attachments")
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) == 8
        assert (
            result[0].file_name
            == "konstytucja-3-maja-czy-mogla-uratowac-i-rzeczpospolita-historie-jak-z-ksiazki-trojka.mp3"
        )

    def test_audiobook(self):
        """https://www.polskieradio.pl/podcast/ziemia-obiecana-wladyslaw-stanislaw-reymont,594"""
        # Given
        given_page_data = read_compressed_demo_data("audiobook")
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_podcasts_episodes_escaped(self):
        # Given
        given_page_data = read_compressed_demo_data("podcasts_episodes_escaped")
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_podcasts_escaped(self):
        # Given
        given_page_data = read_compressed_demo_data("podcasts_escaped")
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
        given_page_data = read_compressed_demo_data("jedynka")
        # When
        result = PrDlCrawl._get_podcasts_v2(given_page_data)
        # Then
        assert len(result) > 0

    def test_polskieradio24(self):
        """url: https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie"""
        # Given
        given_page_data = read_compressed_demo_data("polskieradio24")
        # When
        result = PrDlCrawl._get_podcasts_data_media(
            given_page_data,
            "https://polskieradio24.pl/artykul/2794550,bitwa-pod-tannenbergiem-najdotkliwsza-kleska-rosji-w-wielkiej-wojnie",
        )
        # Then
        assert len(result) == 1
        assert result[0].url == "https://static.prsa.pl/351fd590-234a-4364-8061-38546a26df45.mp3"
