import requests
import time
import polars as pl
from bs4 import BeautifulSoup

petscan_url = "https://petscan.wmcloud.org/?search_wiki=&since_rev0=&labels_any=&active_tab=tab_categories&min_identifiers=&max_identifiers=&max_statements=&show_disambiguation_pages=both&wikidata_prop_item_use=&output_compatability=catscan&language=es&manual_list_wiki=&sortorder=ascending&max_age=&smaller=&combination=subset&depth=0&project=wikipedia&max_sitelink_count=&templates_any=&page_image=any&namespace_conversion=keep&search_max_results=500&ores_prob_to=&outlinks_yes=&cb_labels_yes_l=1&minlinks=&langs_labels_yes=&common_wiki_other=&interface_language=es&templates_no=&cb_labels_any_l=1&common_wiki=auto&show_soft_redirects=both&sitelinks_any=&min_sitelink_count=&wpiu=any&after=&links_to_all=&categories=Personajes_de_X-Men&langs_labels_any=&cb_labels_no_l=1&doit=&interface_language=es"

petscan_resp = requests.get(petscan_url)
if petscan_resp.status_code == 200:
    petscan_text = petscan_resp.text
    petscan_soup = BeautifulSoup(petscan_text)
else:
    petscan_resp.status_code

links = petscan_soup.find_all(class_="link_container")
links_list = []

for i in links:
    links_list.append(
        dict(nombre=i.find("a").text, url=i.find(class_="pagelink").get("href"))
    )

wiki_links = (
    pl.DataFrame(links_list)
    .filter(pl.col("url").str.contains("Categor").not_())
    .sort(pl.col("nombre"))
).with_columns(titulo=pl.col("url").str.extract("wiki\\/(.*)"))

# Get wikidata ids
# access token created at:
# https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth2

with open("access_token.txt") as token_file:
    access_token = token_file.read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}

titles = wiki_links.get_column("titulo")
wikidata_ids = []
wait_time = 0.15

for title in titles:
    print(f"Waiting for {title}")
    time.sleep(wait_time)
    link_resp = requests.get(
        f"https://es.wikipedia.org/api/rest_v1/page/html/{title}", headers=headers
    )
    if link_resp.status_code == 200:
        sopa = BeautifulSoup(link_resp.text)
        wikidata_id = sopa.find(class_="uid").text
    else:
        wikidata_id = "None"
    wikidata_ids.append(wikidata_id)

wiki_links = wiki_links.with_columns(wikidata_id=pl.Series(wikidata_ids))

wiki_links.write_parquet("scrape/wiki_links.parquet")
