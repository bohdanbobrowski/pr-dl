import argparse

from prdl.prdl import PrDlCrawl, PrDlSearch


def check_command_arguments(args):
    if len(args) > 1:
        return True
    return False


def check_valid_url(url: str) -> bool:
    for pattern in [
        "https://www.polskieradio24.pl",
        "https://polskieradio24.pl",
        "https://www.polskieradio.pl",
        "https://polskieradio.pl",
    ]:
        if url.startswith(pattern):
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
        polish_radio_downloader = PrDlSearch(args.url_or_search, args.all, args.forced_search)
    polish_radio_downloader.start()


if __name__ == "__main__":
    main()
