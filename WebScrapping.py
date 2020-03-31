import requests
from urllib.parse import urlparse, urljoin
import pandas as pd
from html.parser import HTMLParser
import urllib.request
import urllib
import re
import codecs
import argparse
import sys
from typing import TypeVar

AnyStr = TypeVar('AnyStr', str, bytes)


def webScrapping(IN, TYPE, CRAWL, z) -> None:# Get base links
    # Classe parser qui trouver les a href dans le html
    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
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
    to_visit = [IN]
    outlinks = []
    visited = {}
    external_visited = {}
    links = []
    deadLinks = []
    toCrawl = True

    if TYPE == 'h':
        parser = MyHTMLParser()
        f = codecs.open(IN, "r", "utf-8")
        html = str(f.read())
        f.close()
        links = []
        links = re.findall(
            "https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:[\w\-]+\.*)+\w+)(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?", html)
        parser.feed(html)

        for link in links:
            if link not in outlinks and link not in visited.keys():
                outlinks.append(link)

    else:
        # Pendant qu'il y a encore des liens dans la variable to_visit
        base = urlparse(IN).netloc
        while to_visit and toCrawl:
            # On extrait un lien à la fois
            l = to_visit.pop()
            print(l)
            url = urljoin(IN, l)

            # On regarde si ce lien existe et on ajoute son status code à la struct des liens visités
            try:
                r = requests.get(url)
                visited[l] = r.status_code
            except:
                visited[l] = None
            # Si le lien existe:
            if r.status_code == 200:
                # On parse le html et on applique notre regex pour trouvez tous les liens
                parser = MyHTMLParser()
                f = urllib.request.urlopen(l)
                html = str(f.read())
                f.close()
                links = []
                links = re.findall("https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:[\w\-]+\.*)+\w+)(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?", html)
                parser.feed(html)

                for link in links:
                    parsed_link = urlparse(link)
                    loc = parsed_link.netloc
                    joined_url = urljoin(IN, link)
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

                    #Si la loc est différente, c'est donc un lien externe:
                    else:
                        # Vérifier les doublons
                        if link not in outlinks and link not in visited.keys():
                            outlinks.append(link)

                if CRAWL == 'False':
                    toCrawl = False
                    while to_visit:
                        # On regarde un lien à la fois
                        l = to_visit.pop()
                        print(l)
                        # On essaye d'y accéder dans un délais inférieur de 1 secondes
                        try:
                            print("trying")
                            r = requests.get(l, timeout=2)
                            visited[l] = r.status_code
                        # Si on n'y arrive pas, on considère le lien mort
                        except:
                            print("except")
                            deadLinks.append(l)
                            visited[l] = None

    # On vérifie ensuite le status de tous les liens externes afin de déterminer ceux qui ne sont pas morts
    print("Checking status of links")
    # Tant quil y a des liens dans outlinks
    while outlinks:
        # On regarde un lien à la fois
        l = outlinks.pop()
        print(l)
        # On essaye d'y accéder dans un délais inférieur de 2 secondes
        try:
            print("trying")
            r = requests.get(l, timeout=2)
            external_visited[l] = r.status_code
        # Si on n'y arrive pas, on considère le lien mort
        except:
            print("except")
            deadLinks.append(l)
            external_visited[l] = None

    # Création d'un DataFrame
    s = pd.Series(visited, name='Response', dtype=object)
    s.index.name = 'URL'
    df1 = pd.DataFrame(s)
    df1['Type'] = 'Internal'

    s = pd.Series(external_visited, name='Response')
    s.index.name = 'URL'
    df2 = pd.DataFrame(s)
    df2['Type'] = 'External'

    results = pd.concat([df1, df2])
    results.to_csv('link_report_' + str(z) + '.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WebCrawler')

    parser.add_argument('--IN', action="store", nargs='+', help="Specifiy the url(s) or the path to the HTML file(s) given in a list [link1, link2, ...]")
    parser.add_argument('--TYPE', action="store", nargs='+', help="Select input type (false: default to u: URL, h: html. Specify in a list")
    parser.add_argument('--CRAWL', action="store", nargs='+', dest="CRAWL", help="Specify if the program should Crawl(True) or not. Crawling will be disabled for local HTML files. Specify in a list")

    opt = parser.parse_args([
        '--IN', ['tal.html'],
        '--TYPE', ['h'],
        '--CRAWL', ['True']
                             ])
    assert len(opt.IN) == len(opt.TYPE) == len(opt.CRAWL), "Input arguments must have the same length"

    for i in range(len(opt.IN)):
        webScrapping(opt.IN[i], opt.TYPE[i], opt.CRAWL[i], i)
