import json
import reqchars as rc
import pandas as pd
from pandas import DataFrame 

SP_CAT = "P2563"

with open("x_men_ents.txt") as file:
    xson = json.loads(file.read())

x_entities_all = dict()

for i in xson:
    x_entities_all.update(i["entities"])

x_entities = x_entities_all.copy()

to_remove = filter(lambda x: len(x) < 4, list(x_entities_all.keys()))
for i in list(to_remove):
    x_entities.pop(i)


sp_unique = []

for i in x_entities.values():
    sp = i.get("claims").get(SP_CAT)
    if sp is not None:
        sp_id = (
            sp[0]
            .get("mainsnak")
            .get("datavalue")
            .get("value")
            .get("id")
            )
        if sp_id not in sp_unique:
            sp_unique.append(sp_id)

sp_unique_groups = "|".join(sp_unique)

sp_unique_ents = rc.get_entity(sp_unique_groups, "id")

sp_unique_list = []

for i in sp_unique:
    sp_props = sp_unique_ents.get("entities").get(i)
    ent_props = {
        "id": sp_props["id"],
        "nombre": sp_props["labels"]["es"]["value"],
        "descripcion": sp_props["descriptions"]["es"]["value"],
        "idioma": sp_props["descriptions"]["es"]["language"],
        "wiki_link": sp_props["sitelinks"].get("eswiki", {}).get("title")
    }
    sp_unique_list.append(ent_props)

DataFrame(sp_unique_list).to_csv("superpowers.csv", encoding="utf-8", index=False)