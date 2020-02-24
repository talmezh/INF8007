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


def webScrapping(URL, HTML, CRAWL):# Get base links
    # Classe parser qui trouver les a href dans le html
    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == "a":
                for name, value in attrs:
                    if name == "href":
                        # Une fois trouvé, le lien est nettoyé afin d'éliminer les faux positifs
                        if value.find(';'):
                            continue
                        else:
                            value = value.replace("\\", '')
                            value = value.replace("\"", '')
                            value = value.replace("'", '')
                            links.append(value)
    # Trouver le lien de base
    base = urlparse(URL).netloc

    to_visit = [URL]
    outlinks = []
    visited = {}
    external_visited = {}
    links = []


    print("Extracting URLs")
    # Pendant qu'il y a encore des liens dans la variable to_visit
    while to_visit:
        # On extrait un lien à la fois
        l = to_visit.pop()
        print(l)
        url = urljoin(URL, l)

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
            links = re.findall("https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:\w+\.)+\w+)(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?", html)
            parser.feed(html)

            for link in links:
                parsed_link = urlparse(link)
                loc = parsed_link.netloc
                joined_url = urljoin(URL, link)
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

    # On vérifie ensuite le status de tous les liens externes afin de déterminer ceux qui ne sont pas morts
    print("Checking status of links")
    deadLinks = []
    # Tant quil y a des liens dans outlinks
    while outlinks:
        # On regarde un lien à la fois
        l = outlinks.pop()
        print(l)
        # On essaye d'y accéder dans un délais inférieur de 1 secondes
        try:
            print("trying")
            r = requests.get(l, timeout=1)
            external_visited[l] = r.status_code
        # Si on n'y arrive pas, on considère le lien mort
        except:
            print("except")
            deadLinks.append(l)
            external_visited[l] = None

    # Création d'un DataFrame
    s = pd.Series(visited, name='Response')
    s.index.name = 'URL'
    df1 = pd.DataFrame(s)
    df1['Type'] = 'Internal'

    s = pd.Series(external_visited, name='Response')
    s.index.name = 'URL'
    df2 = pd.DataFrame(s)
    df2['Type'] = 'External'

    results = pd.concat([df1, df2])
    results.to_csv('link_report.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='WebCrawler')

    parser.add_argument('--URL', action="store", help="Specifiy the base link (required)")
    parser.add_argument('--HTML', action="store", default=False, dest="HTML", help="Specify the HTML file, defaults to false")
    parser.add_argument('--CRAWL', action="store_true", default=False, dest="CRAWL", help="Specify if the program should Crawl(True) or not")
    parser.add_argument('--InputType', action="store", default="u", dest="InputType", help="Select input type (false: default to u: URL, h: html, l: liste url, f: liste fichiers)")
    opt = parser.parse_args(['--URL', 'https://deniscorbin1.wordpress.com/', '--HTML', 'test.html', '--CRAWL', '--InputType', 'h'])
    if opt.InputType =='u' or  opt.InputType =='h':
        webScrapping(opt.URL, opt.HTML, opt.CRAWL)
    else:
        for stuff in opt.IRL:
            webScrapping(opt.URL, opt.HTML, opt.CRAWL)
    #print(parser.parse_args("URL"))
    #site = codecs.open("/home/decora/Downloads/Denis Corbin _ Je suis étudiant en sciences de la nature au Cégep de Terrebonne.html", 'r')
    #site = 'https://lesvolsdalexi.com/'
    #webScrapping(site)
    # Donner le liens comme argument en input
    #webScrapping(sys.argv[1])
