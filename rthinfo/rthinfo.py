#!/usr/bin/env python

import requests, argparse, time, os, sys
from bs4 import BeautifulSoup
from prettytable import from_html_one, from_html, PLAIN_COLUMNS, ORGMODE, SINGLE_BORDER, DOUBLE_BORDER
from tabulate import tabulate
import textwrap

PROGNAME = "rthinfo"
VERSION = "0.1.0"
AUTHOR = "Copyright (C) 2022, by Michael John"
DESC = "Fetch and show data from rth.info"
EPILOG="search criteria:"

def build_url(option):
    if option == True:
        url = "https://www.rth.info/stationen.db/stationen.php"
        url += "?category="
    return url

def get_data(url, quiet=False):
    if not quiet:
        print(f"Fetching {url}")
    response = requests.get(url)
    return response.text.replace('\n', '').replace('Specials', '') # .replace('Specials', '</th><th></th><th></th><th></th></tr>')

def parse_data(data, table_id):
    soup = BeautifulSoup(data, 'lxml')
    table = soup.find_all('table')[table_id]
    for span in table.find_all("span"):
        if span.attrs.get('class') is not None and "js-flag-replace" in span.attrs.get('class'):
            span.replaceWith(span, ", ")
    for span in table.find_all("span"):
        if span.attrs.get('class') is not None and "d-md-none" in span.attrs.get('class'):
            span.decompose()
        else:
            span.replaceWithChildren()
    for a in table.find_all("a"):
        a.replaceWithChildren()
    for abbr in table.find_all("abbr"):
        abbr.replaceWithChildren()
    for th in table.find_all("th"):
        if th.attrs.get('colspan') == "5":
            th.colspan = 0
    return table

def print_table(data, filter="", quiet=False):
    if filter is None:
        filter = ""
    for tr in data.find_all_next("tr"):
        try:
            if "Stadt" in tr.contents[3].text:
                continue
            if filter not in tr.contents[3].text: # and "Rufname" not in tr.contents[3].text:
                tr.decompose()
        except IndexError:
            tr.decompose()
            continue
    table = from_html_one(str(data))
    table.set_style(SINGLE_BORDER)
    table.align = "l"
    #table.fields = ['Rufname', 'Stadt', 'Stationierungsort', 'Art der Station', 'Betreiber', 'Typ', '', "'", "''", "'''", "''''"  ]

    print(table.get_string(start=0))
    if not quiet:
        if table.rowcount > 0:
            print(f"Number of results: {table.rowcount}")
        else:
            print(f"No results for search criteria.")

def main():
    start = time.time()

    parser = argparse.ArgumentParser(prog=PROGNAME, description=DESC)  #, epilog=EPILOG + criteria_str)
    parser.add_argument('-n', dest='callsign', help='search for callsign/name of heli, i.e. `Christoph 31`', type=str)
    parser.add_argument('-c', dest='country', help='search for country or city of deployment, i.e. `DE` or `Lausanne`', type=str)
    parser.add_argument('-r', dest='registration', help='search for registration of heli, i.e. `D-HXCA`', type=str)
    parser.add_argument('-q', '--quiet', help='suppress output', action='store_true')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + VERSION + ' ' + AUTHOR)

    args = parser.parse_args()
    quiet = vars(args)["quiet"]
    if not quiet:
        print(str(args).replace("Namespace", "Options"))
    
    data = get_data(build_url(True), quiet)
    parsed = parse_data(data, table_id=0)
    print_table(parsed, filter=vars(args)["country"], quiet=vars(args)["quiet"])

    end = time.time()
    if not vars(args)["quiet"]:
        print('[{:2.3} seconds elapsed]'.format((end - start)))
