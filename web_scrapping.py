#!/usr/bin/env Python
""" This script is used to crawl website(s) and html(s)"""
import sys
import argparse
import codecs
import re
import urllib
import urllib.request
from abc import ABC
from html.parser import HTMLParser
from typing import Dict, List
from urllib.parse import urlparse, urljoin
import pylint  # type: ignore
import pandas as pd  # type: ignore
import requests

def eprint(message: str):
    """ Writes message to std:err """
    print(message, file=sys.stderr)


def regex(html: str) -> List[str]:
    """ Fonction pure: Uses the Regex to extract links on the given parsed HTML """
    reg = r"https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:[\w\-]+\.*)+\w+)" \
          r"(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?"
    return re.findall(reg, html)


def update_args(opt):
    """ Fonction pure: Updates the args of opt """
    opt_out: List[List[str, str, str]] = []
    file1 = open(opt.IN[0], 'r')
    lines = file1.readlines()
    for line in lines:
        opt_out.append(line.strip().split(','))
    return opt_out


def is_href(name: str) -> bool:
    """ Fonction pure: verify is start tag contains href """
    return name == "href"


def web_scrapping(in_arg: str, type_arg: str, crawl_arg: str, i_arg: int) -> None:  # Get base links
    """Scrape the given input and write to files the status of all found links"""

    # Classe parser qui trouver les a href dans le html
    class MyHTMLParser(HTMLParser, ABC):
        """ This class parse a HTML file and returns all a href"""
        def handle_starttag(self, tag: str, attrs) -> None:
            if tag == "a":
                for name, value in attrs:
                    if is_href(name):
                        # Une fois trouvé, le lien est nettoyé afin d'éliminer les faux positifs
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

    if type_arg.endswith('h'):
        # Lecture du fichier
        file = codecs.open(in_arg, "r", "utf-8")
        try:
            html = str(file.read())
            file.close()
        except:
            eprint("Cannot open input file %s" % in_arg)
        # Extraction des liens
        links = regex(html)
        # Les liens sont considérés externes car on n'a pas le domaine
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
                eprint("No response from %s. Cannot obtain status code" % url)
                visited[link] = 0
            # Si le lien existe:
            try:
                req
            except NameError:
                eprint("Main domain is unreachable, are you sure it's online?")
            else:
                if req.status_code == 200:
                    # On parse le html et on applique notre regex pour trouvez tous les liens
                    parser_local = MyHTMLParser()
                    try:
                        file = urllib.request.urlopen(link)
                        html = str(file.read())
                        file.close()
                    except:
                        eprint("Unable to read html code from %s" % link)
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

                    if crawl_arg.endswith('False'):
                        to_crawl = False
                        while to_visit:
                            # On regarde un lien à la fois
                            link = to_visit.pop()
                            print(link)
                            # On essaye d'y accéder dans un délais inférieur de 1 secondes
                            try:
                                req = requests.get(link, timeout=2)
                                visited[link] = req.status_code
                            # Si on n'y arrive pas, on considère le lien mort
                            except:
                                eprint("No response from %s. Cannot obtain status code" % link)
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
            req = requests.get(link, timeout=2)
            external_visited[link] = req.status_code
        # Si on n'y arrive pas, on considère le lien mort
        except:
            eprint("No response fromexternal link %s. Cannot obtain status code" % link)
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
    # Linter
    OPTIONS = '-enable=all'
    OPTIONS += 'reports=y'
    STDOUT, STDERR = pylint.epylint.py_run('web_scrapping.py' + ' ' + OPTIONS, return_std=True)
    print(STDOUT.getvalue())
    print(STDERR.getvalue())

    # Parser
    PARSER = argparse.ArgumentParser(description='WebCrawler')

    PARSER.add_argument('--IN', action="store", nargs='+',
                        help="Specifiy the url(s) or the path to the HTML file(s)"
                             " given in a list [link1, link2, ...]")
    PARSER.add_argument('--TYPE', action="store", nargs='+',
                        help="Select input type (u: URL, h: html, f: file)"
                             " Specify in a list")
    PARSER.add_argument('--CRAWL', action="store", nargs='+', dest="CRAWL",
                        help="Specify if the program should Crawl(True) or not. "
                             "Crawling arg be ignored for local HTML files."
                             "Specify in a list fashion. Not needed for files")

    OPT = PARSER.parse_args()

    # URLs et fichiers htlm sont dans un fichier:
    if OPT.TYPE == ['f']:
        if not len(OPT.IN) == len(OPT.TYPE):
            eprint("Input arguments must have the same length")
        else:
            TO_PARSE = update_args(OPT)
            for i in range(len(TO_PARSE)):
                OPT = PARSER.parse_args([
                    '--IN', TO_PARSE[i][0],
                    '--TYPE', TO_PARSE[i][1],
                    '--CRAWL', TO_PARSE[i][2]
                ])
                assert len(OPT.IN) == len(OPT.TYPE) == len(OPT.CRAWL), \
                    "Input arguments must have the same length"
                web_scrapping(OPT.IN[0], OPT.TYPE[0], OPT.CRAWL[0], i)
    else:
        if not len(OPT.IN) == len(OPT.TYPE):
            eprint("Input arguments must have the same length")
        else:
            for i in range(len(OPT.IN)):
                web_scrapping(OPT.IN[i], OPT.TYPE[i], OPT.CRAWL[i], i)
