import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

# Get base links
site = 'https://lesvolsdalexi.com/'
base = urlparse(site).netloc

to_visit = [site]
outlinks = []
visited = {}
external_visited = {}


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
        soup = BeautifulSoup(r.content, 'html.parser')
        links = [l['href'] for l in soup.find_all('a', href=True)]
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
while outlinks:
    l = outlinks.pop()

    try:
        r = requests.get(l)
        external_visited[l] = r.status_code
    except:
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