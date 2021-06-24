#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from prdl.prdl import PrDlCrawl, PrDlSearch
import sys


def checkCommandArcguments(args):
    if len(args) > 1:
        return True
    return False

def checkValidUrl(arg):
    urls = [
        "https://polskieradio24.pl",
        "https://www.polskieradio.pl",
        "http://www.polskieradio.pl"
    ]
    for url in urls:
        if arg.find(url) == 0:
            return True
    return False

def printHelp():
    print("PRDL - Polskie Radio Downloader")
    print("")
    print("python pr-dl-cli.pl [url] [-t] [-f]")
    print("")

def main(args = None):
    if not args:
        args = sys.argv
    if checkCommandArcguments(args):
        SAVE_ALL = False
        FORCED_SEARCH =False
        if '-t' in args or '-T' in args:
            SAVE_ALL = True
        if '-f' in args or '-F' in args:
            FORCED_SEARCH = True
        if checkValidUrl(args[1]):
            prdl = PrDlCrawl(args[1], SAVE_ALL)
        else:
            prdl = PrDlSearch(args[1], SAVE_ALL, FORCED_SEARCH)
        prdl.start()
    else:
        printHelp()

