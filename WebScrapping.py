import requests
from urllib.parse import urlparse, urljoin
import pandas as pd
from html.parser import HTMLParser
import urllib.request
import re


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if value.find(';'):
                        continue
                    else:
                        value = value.replace("\\", '')
                        value = value.replace("\"", '')
                        value = value.replace("'", '')
                        links.append(value)

# Get base links
site = 'https://deniscorbin1.wordpress.com/'
base = urlparse(site).netloc

to_visit = [site]
outlinks = []
visited = {}
external_visited = {}
links = []


print("Extracting URLs")
while to_visit:
    l = to_visit.pop()
    print(l)
    url = urljoin(site, l)

    try:
        r = requests.get(url)
        visited[l] = r.status_code

    except:
        visited[l] = None

    if r.status_code == 200:
        parser = MyHTMLParser()
        f = urllib.request.urlopen(l)
        html = str(f.read())
        f.close()
        links = []
        import time
        #t = time.time()
        links = re.findall("https?://?(?:(?:\w+\.)+[\w:]+\@)?(?:(?:\w+\.)+\w+)(?::\w+)?(?:/[\w\.\-]+)*/?(?:\?[\w=&]+)?(?:#\w+)?", html)
        #print(time.time()-t)
        parser.feed(html)

        for link in links:
            parsed_link = urlparse(link)
            loc = parsed_link.netloc
            path = parsed_link.path
            joined_url = urljoin(site, link)
            if loc == '':
                if joined_url not in to_visit and joined_url not in visited.keys():
                    to_visit.append(joined_url)

            elif loc == base:
                if link not in to_visit and link not in visited.keys():
                    to_visit.append(link)

            else:
                if link not in outlinks and link not in visited.keys():
                    outlinks.append(link)

# check the status of external links
print("Checking status of links")
deadLinks = []
while outlinks:
    l = outlinks.pop()
    print(l)

    try:
        print("trying")
        r = requests.get(l, timeout=1)
        external_visited[l] = r.status_code
    except:
        print("except")
        deadLinks.append(l)
        external_visited[l] = None

# Create a DataFrame
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
    print(1)