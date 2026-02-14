import requests
import time
import polars as pl

# Get wikidata ids
# access token created at:
# https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth2

with open("access_token.txt") as token_file:
    access_token = token_file.read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {access_token}",
}

wiki_links = pl.read_parquet("scrape/wiki_links.parquet")
wikidata_ids = wiki_links.get_column("wikidata_id")

# P463  team
# P170  creator
# P2563 power
property_id = "P463"
wait_time = 0.15

teams_list = []

for wikidata_id in wikidata_ids:
    print(f"Waiting for {wikidata_id}")
    time.sleep(wait_time)
    wikidata_url = f"https://www.wikidata.org/w/api.php?action=wbgetclaims&format=json&entity={wikidata_id}&property={property_id}&formatversion=2"
    data_resp = requests.get(wikidata_url, headers=headers)
    data_claims = data_resp.json().get("claims").get(property_id)
    if data_claims is not None:
        teams = [
            i.get("mainsnak").get("datavalue").get("value").get("id")
            for i in data_claims
        ]
    else:
        teams = ["None"]
    teams_list.append(teams)

nombres = wiki_links.get_column("nombre")

pl.read_parquet("data/char_data.parquet")

equipos_lista = []

for i, j in zip(nombres, teams_list):
    equipos_lista.append(pl.DataFrame({"nombre":i, "equipo_id":j}))

equipos_df = pl.concat(equipos_lista)

wiki_links.join(equipos_df, how="inner", on="nombre").write_parquet("scrape/wiki_links.parquet")