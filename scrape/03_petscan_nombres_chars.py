import requests
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

wiki_links = pl.DataFrame(links_list).filter(pl.col("url").str.contains("Categor").not_()).sort(pl.col("nombre"))

wiki_links.write_parquet("scrape/wiki_links.parquet")