#!/usr/bin/env Python
""" This script is used to crawl website(s) and html(s)"""

import argparse
import codecs
import re
import urllib
import urllib.request
from abc import ABC
from html.parser import HTMLParser
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse, urljoin
import pandas as pd  # type: ignore
import pylint   # type: ignore
import requests


def regex(html: str) -> List[str]:
    """ Uses the following Regex to extract links on the given parsed HTML"""
    reg = r"https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:[\w\-]+\.*)+\w+)" \
          r"(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?"
    return re.findall(reg, html)


def web_scrapping(in_arg: str, type_arg: str, crawl_arg: str, i_arg: int) -> None:  # Get base links
    """Scrape the given input and write to files the status of all found links"""
    # Classe parser qui trouver les a href dans le html
    class MyHTMLParser(HTMLParser, ABC):
        """ This class parse a HTML file and returns all a href"""
        def handle_starttag(self, tag: str, attrs) -> None:
            if tag == "a":
                for name, value in attrs:
                    if name == "href":
                        # Une fois trouvé, le lien est nettoyé afin d'éliminer les faux positifs
                        # if value.find(';') != -1:
                        #     continue
                        # else:
                        value = value.replace("\\", '')
                        value = value.replace("\"", '')
                        value = value.replace("'", '')
                        links.append(value)

    # Trouver le lien de base
    to_visit: List[str] = [in_arg]
    visited: Dict[str, int] = {}
    external_visited: Dict[str, int] = {}
    links: List[str] = []
    outlinks: List[str] = []
    deadlinks: List[str] = []
    to_crawl = True

    if type_arg == 'h':
        file = codecs.open(in_arg, "r", "utf-8")
        html = str(file.read())
        file.close()
        links = regex(html)
        for link in links:
            if link not in outlinks and link not in visited.keys():
                outlinks.append(link)

    else:
        # Pendant qu'il y a encore des liens dans la variable to_visit
        base = urlparse(in_arg).netloc
        while to_visit and to_crawl:
            # On extrait un lien à la fois
            link = to_visit.pop()
            print(link)
            url = urljoin(in_arg, link)

            # On regarde si ce lien existe et on ajoute son status code à visited
            try:
                req = requests.get(url, timeout=2)
                visited[link] = req.status_code
            except:
                visited[link] = 0
            # Si le lien existe:
            if req.status_code == 200:
                # On parse le html et on applique notre regex pour trouvez tous les liens
                parser_local = MyHTMLParser()
                file = urllib.request.urlopen(link)
                html = str(file.read())
                file.close()
                links = []
                links = regex(html)
                parser_local.feed(html)

                for link in links:
                    parsed_link = urlparse(link)
                    loc = parsed_link.netloc
                    joined_url = urljoin(in_arg, link)
                    # Si la loc est vide:
                    if loc == '':
                        # Vérifier les doublons
                        if joined_url not in to_visit and joined_url not in visited.keys():
                            to_visit.append(joined_url)

                    # Si la loc est égale à la base:
                    elif loc == base:
                        # Vérifier les doublons
                        if link not in to_visit and link not in visited.keys():
                            to_visit.append(link)

                    # Si la loc est différente, c'est donc un lien externe:
                    else:
                        # Vérifier les doublons
                        if link not in outlinks and link not in visited.keys():
                            outlinks.append(link)

                if crawl_arg == 'False':
                    to_crawl = False
                    while to_visit:
                        # On regarde un lien à la fois
                        link = to_visit.pop()
                        print(link)
                        # On essaye d'y accéder dans un délais inférieur de 1 secondes
                        try:
                            print("trying")
                            req = requests.get(link, timeout=2)
                            visited[link] = req.status_code
                        # Si on n'y arrive pas, on considère le lien mort
                        except:
                            print("except")
                            deadlinks.append(link)
                            visited[link] = 0

    # On vérifie le status de tous les liens externes afin de trouver ceux qui ne sont pas morts
    print("Checking status of links")
    # Tant quil y a des liens dans outlinks
    while outlinks:
        # On regarde un lien à la fois
        link = outlinks.pop()
        print(link)
        # On essaye d'y accéder dans un délais inférieur de 2 secondes
        try:
            print("trying")
            req = requests.get(link, timeout=2)
            external_visited[link] = req.status_code
        # Si on n'y arrive pas, on considère le lien mort
        except:
            print("except")
            deadlinks.append(link)
            external_visited[link] = 0

    # Création d'un DataFrame
    serie = pd.Series(visited, name='Response', dtype=object)
    serie.index.name = 'URL'
    df1 = pd.DataFrame(serie)
    df1['Type'] = 'Internal'

    serie = pd.Series(external_visited, name='Response')
    serie.index.name = 'URL'
    df2 = pd.DataFrame(serie)
    df2['Type'] = 'External'

    results = pd.concat([df1, df2])
    results.to_csv('link_report_' + str(i_arg) + '.csv')


if __name__ == '__main__':
    OPTIONS = '-enable=all'
    OPTIONS += 'reports=y'

    STDOUT, STDERR = pylint.epylint.py_run('web_scrapping.py' + ' ' + OPTIONS, return_std=True)
    print(STDOUT.getvalue())
    print(STDERR.getvalue())

    PARSER = argparse.ArgumentParser(description='WebCrawler')

    PARSER.add_argument('--IN', action="store", nargs='+',
                        help="Specifiy the url(s) or the path to the HTML file(s)"
                             " given in a list [link1, link2, ...]")
    PARSER.add_argument('--TYPE', action="store", nargs='+',
                        help="Select input type (false: default to u: URL, h: html."
                             " Specify in a list")
    PARSER.add_argument('--CRAWL', action="store", nargs='+', dest="CRAWL",
                        help="Specify if the program should Crawl(True) or not. "
                             "Crawling will be disabled for local HTML files. Specify in a list")

    OPT = PARSER.parse_args([
        '--IN', 'http://localhost:3000/', 'tal.html',
        '--TYPE', 'u', 'h',
        '--CRAWL', 'True', 'False'
    ])
    assert len(OPT.IN) == len(OPT.TYPE) == len(OPT.CRAWL),\
        "Input arguments must have the same length"

    for i in range(len(OPT.IN)):
        web_scrapping(OPT.IN[i], OPT.TYPE[i], OPT.CRAWL[i], i)
