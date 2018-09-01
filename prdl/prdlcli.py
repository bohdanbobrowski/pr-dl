#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prdl import PrDlCrawl, PrDlSearch
import sys

def checkCommandArcguments():
    if len(sys.argv) > 1:
        return True
    return False

def checkValidUrl():
    if sys.argv[1].find("https://www.polskieradio.pl") == 0 or sys.argv[1].find("http://www.polskieradio.pl") == 0:
        return True
    return False

def printHelp():
    print "PRDL - Polskie Radio Downloader"
    print ""
    print "python pr-dl-cli.pl [url] [-t] [-f]"
    print ""

def main():
    if checkCommandArcguments():
        SAVE_ALL = False
        FORCED_SEARCH =False
        if '-t' in sys.argv or '-T' in sys.argv:
            SAVE_ALL = True
        if '-f' in sys.argv or '-F' in sys.argv:
            FORCED_SEARCH = True
        if checkValidUrl():
            prdl = PrDlCrawl(sys.argv[1], SAVE_ALL)
        else:
            prdl = PrDlSearch(sys.argv[1], SAVE_ALL, FORCED_SEARCH)
        prdl.start()
    else:
        printHelp()
