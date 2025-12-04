import argparse

from prdl.prdl import PrDlCrawl, PrDlSearch

POLSKIE_RADIO_SUBDOMAINS = [
    "3pyta.polskieradio.pl",
    "4q.embedder.polskieradio.pl",
    "admins@polskieradio.pl",
    "apiv4.embedder.polskieradio.pl",
    "autodiscover.polskieradio.pl",
    "chopin-test.polskieradio.pl",
    "chopin.polskieradio.pl",
    "cm22.embedder.polskieradio.pl",
    "embedder.polskieradio.pl",
    "fb.polskieradio.pl",
    "ftps.polskieradio.pl",
    "hubs.polskieradio.pl",
    "iar.polskieradio.pl",
    "intranet-test.polskieradio.pl",
    "jedynka.polskieradio.pl",
    "linport.polskieradio.pl",
    "live.embedder.polskieradio.pl",
    "loteria.polskieradio.pl",
    "lukasz.rakowski@polskieradio.pl",
    "lzr2021.polskieradio.pl",
    "mg22.embedder.polskieradio.pl",
    "mobileapi.polskieradio.pl",
    "mojepolskieradio.pl",
    "norwid.polskieradio.pl",
    "npr24.embedder.polskieradio.pl",
    "opal.polskieradio.pl",
    "player.polskieradio.pl",
    "poczta.polskieradio.pl",
    "poczta2.polskieradio.pl",
    "podcasty.polskieradio.pl",
    "polskieradio.pl",
    "postmaster@polskieradio.pl",
    "prkapi.embedder.polskieradio.pl",
    "prkcmstest.embedder.polskieradio.pl",
    "prktest.embedder.polskieradio.pl",
    "redaktor.polskieradio.pl",
    "reportaz.polskieradio.pl",
    "rozewicz.polskieradio.pl",
    "sklep.polskieradio.pl",
    "skleporders.polskieradio.pl",
    "srep.embedder.polskieradio.pl",
    "test-le.polskieradio.pl",
    "test.embedder.polskieradio.pl",
    "testlato.polskieradio.pl",
    "trojka.polskieradio.pl",
    "trojkapyta.polskieradio.pl",
    "www.3pyta.polskieradio.pl",
    "www.chopin.polskieradio.pl",
    "www.embedder.polskieradio.pl",
    "www.jedynka.polskieradio.pl",
    "www.loteria.polskieradio.pl",
    "www.mojepolskieradio.pl",
    "www.norwid.polskieradio.pl",
    "www.podcasty.polskieradio.pl",
    "www.polskieradio.pl",
    "www.prktest.embedder.polskieradio.pl",
    "www.reportaz.polskieradio.pl",
    "www.rozewicz.polskieradio.pl",
    "www.sklep.polskieradio.pl",
    "www.srep.embedder.polskieradio.pl",
    "www.trojka.polskieradio.pl",
    "www.trojkapyta.polskieradio.pl",
]


def check_command_arguments(args):
    if len(args) > 1:
        return True
    return False


def check_valid_url(url: str) -> bool:
    for subdomain in POLSKIE_RADIO_SUBDOMAINS:
        if url.startswith(f"https://{subdomain}") or url.startswith(subdomain):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(prog="prdl", description="Polish Radio Downloader")
    parser.add_argument("url_or_search", type=str, help="Url or search phrase.")
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Save all podcasts without confirmation.",
    )
    parser.add_argument(
        "-f",
        "--forced",
        action="store_true",
        help="Don't trust PR searchengine - show only results with given keyword.",
    )
    args = parser.parse_args()
    if check_valid_url(args.url_or_search):
        polish_radio_downloader = PrDlCrawl(args.url_or_search, args.all)
    else:
        polish_radio_downloader = PrDlSearch(args.url_or_search, args.all, args.forced)
    polish_radio_downloader.start()


if __name__ == "__main__":
    main()
