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


def get_entities(
    id_list: list,
    label: str,
):
    entities_url = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={wikidata_ids}&props=sitelinks%7Clabels&languages=es%7Cen&sitefilter=eswiki%7Cenwiki&formatversion=2"
    divisiones = []
    column_label = f"{label}_id"

    for i in range(0, len(id_list), 50):
        grupo = id_list[i : i + 50]
        divisiones.append("%7C".join(grupo))

    entities_df_list = []
    for division in divisiones:
        print("Waiting...")
        time.sleep(0.15)
        entities_resp = requests.get(
            entities_url.format(wikidata_ids=division), headers=headers
        )
        ent_json = entities_resp.json().get("entities")

        entities_list = []
        for wd_id in division.split("%7C"):
            entity_dict = {
                column_label: wd_id,
                "nombre_es": ent_json[wd_id]
                .get("labels")
                .get("es", {})
                .get("value", "None"),
                "nombre_en": ent_json[wd_id]
                .get("labels")
                .get("en", {})
                .get("value", "None"),
                "link_eswiki": ent_json[wd_id]
                .get("sitelinks")
                .get("eswiki", {})
                .get("title", "None"),
                "link_enwiki": ent_json[wd_id]
                .get("sitelinks")
                .get("enwiki", {})
                .get("title", "None"),
            }
            entities_list.append(entity_dict)

        entities_df_list.append(pl.DataFrame(entities_list))
    entities_df = pl.concat(entities_df_list)
    return entities_df


p_team = "P463"
p_power = "P2563"
p_creator = "P170"

wiki_links = pl.read_parquet("scrape/wiki_links.parquet")
wikidata_ids = list(wiki_links.get_column("wikidata_id"))
nombres = list(wiki_links.get_column("nombre"))

df_team = get_properties(p_team, "team", wikidata_ids, nombres, headers)
df_power = get_properties(p_power, "power", wikidata_ids, nombres, headers)
df_creator = get_properties(p_creator, "creator", wikidata_ids, nombres, headers)


team_ids = list(
    df_team.unique("team_id").filter(pl.col("team_id") != "None").get_column("team_id")
)
power_ids = list(
    df_power.unique("power_id")
    .filter(pl.col("power_id") != "None")
    .get_column("power_id")
)
creator_ids = list(
    df_creator.unique("creator_id")
    .filter(pl.col("creator_id") != "None")
    .get_column("creator_id")
)

df_e_team = get_entities(team_ids, "team")
df_e_power = get_entities(power_ids, "power")
df_e_creator = get_entities(creator_ids, "creator")

df_team.write_parquet("scrape/wiki_p_team.parquet")
df_power.write_parquet("scrape/wiki_p_power.parquet")
df_creator.write_parquet("scrape/wiki_p_creator.parquet")

df_e_team.write_parquet("scrape/wiki_e_team.parquet")
df_e_power.write_parquet("scrape/wiki_e_power.parquet")
df_e_creator.write_parquet("scrape/wiki_e_creator.parquet")
