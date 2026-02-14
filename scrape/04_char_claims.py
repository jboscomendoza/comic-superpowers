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


def get_properties(
    property_id: str, label: str, entity_ids: list, nombres: list, headers: dict
) -> pl.DataFrame:
    property_list = []
    wait_time = 0.15
    column_label = f"{label}_id"
    for wikidata_id in entity_ids:
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
        property_list.append(teams)
    property_nombres = []
    for i, j in zip(nombres, property_list):
        property_nombres.append(pl.DataFrame({"nombre": i, column_label: j}))
    property_df = pl.concat(property_nombres)
    return property_df


p_team = "P463"
p_power = "P2563"
p_creator = "P170"

wiki_links = pl.read_parquet("scrape/wiki_links.parquet")
wikidata_ids = list(wiki_links.get_column("wikidata_id"))
nombres = list(wiki_links.get_column("nombre"))

df_team = get_properties(p_team, "team", wikidata_ids, nombres, headers)
df_power = get_properties(p_power, "power", wikidata_ids, nombres, headers)
df_creator = get_properties(p_creator, "creator", wikidata_ids, nombres, headers)

df_team.write_parquet("scrape/wiki_p_team.parquet")
df_power.write_parquet("scrape/wiki_p_power.parquet")
df_creator.write_parquet("scrape/wiki_p_creator.parquet")
