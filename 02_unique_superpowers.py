import json
import reqchars as rc
from pandas import DataFrame 

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

def get_id(entity, what_id):
    info_unique = []
    info = entity.get("claims").get(what_id)
    if info is not None:
        for i in info:
            info_id= (
                i
                .get("mainsnak")
                .get("datavalue", {})
                .get("value", {})
                .get("id", None)
                )
            info_unique.append(info_id)
        return info_unique
    else:
        return [None]

super_power = "P2563"
super_power_list = []
gender = "P21"
gender_list = []
teams = "P463"
teams_list = []
universe = "P1080"
universe_list = []


for i in x_entities.values():
    super_power_list.append(get_id(i, super_power))
    gender_list.append(get_id(i, gender))
    teams_list.append(get_id(i, teams))
    universe_list.append(get_id(i, universe))


def get_unique(info_list):
    unique_list = [ip for i_list in info_list for ip in i_list]
    unique_list = set(unique_list)
    unique_list = list(filter(lambda x: x is not None, unique_list))
    return unique_list


sp_unique, gn_unique, tm_unique, un_unique = [
    get_unique(i) for i in [super_power_list, gender_list, teams_list, universe_list]
    ]

gn_groups = "|".join(gn_unique)

sp_unique_ents = rc.get_entity(gn_groups, "id")

gn_unique_list = []

for i in sp_unique:
    sp_props = sp_unique_ents.get("entities").get(i)
    ent_props = {
        "id": sp_props["id"],
        "nombre": sp_props["labels"]["es"]["value"],
        "descripcion": sp_props["descriptions"]["es"]["value"],
        "idioma": sp_props["descriptions"]["es"]["language"],
        "wiki_link": sp_props["sitelinks"].get("eswiki", {}).get("title")
    }
    gn_unique_list.append(ent_props)

#DataFrame(sp_unique_list).to_csv("superpowers.csv", encoding="utf-8", index=False)