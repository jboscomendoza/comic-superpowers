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

def dividir_grupos(lista, cantidad=50):
    divisiones = []
    for i in range(0, len(lista), cantidad):
        x = i
        ls = lista[x:x+cantidad]
        ls = "|".join(ls)
        divisiones.append(ls)
    return divisiones

gn_grupos = dividir_grupos(gn_unique)

gn_unique_ents = rc.get_entity(gn_grupos[0], "id")

gn_unique_list = []

for i in gn_unique:
    gn_props = gn_unique_ents.get("entities").get(i)
    ent_props = {
        "id": gn_props["id"],
        "nombre": gn_props["labels"]["es"]["value"],
        "descripcion": gn_props["descriptions"]["es"]["value"],
        "idioma": gn_props["descriptions"]["es"]["language"],
        "wiki_link": gn_props["sitelinks"].get("eswiki", {}).get("title")
    }
    gn_unique_list.append(ent_props)

#DataFrame(sp_unique_list).to_csv("superpowers.csv", encoding="utf-8", index=False)