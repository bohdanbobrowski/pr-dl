import argparse

from prdl.domains import is_url_valid
from prdl.prdl import PrDlCrawl, PrDlSearch


def check_command_arguments(args):
    if len(args) > 1:
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
        "-d",
        "--debug",
        action="store_true",
        help="Turn on debug mode.",
    )
    parser.add_argument(
        "-f",
        "--forced",
        action="store_true",
        help="Don't trust PR searchengine - show only results with given keyword.",
    )
    args = parser.parse_args()
    if is_url_valid(args.url_or_search):
        polish_radio_downloader = PrDlCrawl(
            url=args.url_or_search,
            save_all=args.all,
            debug=args.debug,
        )
    else:
        polish_radio_downloader = PrDlSearch(
            phrase=args.url_or_search,
            save_all=args.all,
            forced_search=args.forced,
            debug=args.debug,
        )
    polish_radio_downloader.start()


if __name__ == "__main__":
    main()
