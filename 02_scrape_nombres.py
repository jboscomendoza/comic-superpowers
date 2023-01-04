import re
import requests
from bs4 import BeautifulSoup

x_men_url  = "https://en.wikipedia.org/wiki/List_of_X-Men_members"
x_men_resp = requests.get(x_men_url)
x_men_text = x_men_resp.text
x_men_soup = BeautifulSoup(x_men_text)
tablas = x_men_soup.find_all("table", class_="wikitable")

links = []

for tabla in tablas:
    renglones = tabla.find_all("tr")
    for renglon in renglones:
        celdas = renglon.find_all("td")
        for celda in celdas:
            try:
                enlace = celda.find("a").get("href")
                if "wiki" in  enlace:
                    links.append(enlace)
            except:
                pass

links = [re.sub("/wiki/|#.*", "", i)+"\n" for i in links]

wiki_links = list(set(links))
wiki_links.sort()

with open(r"wiki_links.txt", 'w') as file_txt:
    file_txt.writelines(wiki_links)