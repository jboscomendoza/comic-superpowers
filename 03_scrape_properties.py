import time
import reqchars as rc
import pandas as pd


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


def get_unique(info_list):
    unique_list = [ip for i_list in info_list for ip in i_list]
    unique_list = set(unique_list)
    unique_list = list(filter(lambda x: x is not None, unique_list))
    return unique_list

def dividir_grupos(lista, cantidad=50):
    divisiones = []
    for i in range(0, len(lista), cantidad):
        x = i
        ls = lista[x:x+cantidad]
        ls = "|".join(ls)
        divisiones.append(ls)
    return divisiones


def props_dict(lista_unicos):
    unique_list = []
    grupos = dividir_grupos(lista_unicos)
    for grp in grupos:
        unique_ents = rc.get_entity(grp, "id")
        for i in lista_unicos:
            props = unique_ents.get("entities").get(i)
            if props is not None:
                ent_props = {
                    "id": props.get("id"),
                    "nombre": props.get("labels").get("es", {}).get("value"),
                    "descripcion": props.get("descriptions", {}).get("es", {}).get("value"),
                    "idioma": props.get("descriptions", {}).get("es", {}).get("language"),
                    "wiki_link": props.get("sitelinks", {}).get("eswiki", {}).get("title")
                }
                unique_list.append(ent_props)
    return unique_list

super_power = "P2563"
gender = "P21"
teams = "P463"
universe = "P1080"


with open("wiki_links.txt", "r") as links_file:
    x_men = links_file.readlines()
    x_men = [i.rstrip("\n") for i in x_men]


x_men_groups = dividir_grupos(x_men, 25)

x_men_ents = []

for x_men_names in x_men_groups:
    entity_group = rc.get_entity(x_men_names, type="title")
    x_men_ents.append(entity_group)
    # Courtesy sleep
    time.sleep(2)

x_entities_all = dict()

for i in x_men_ents:
    x_entities_all.update(i["entities"])

x_entities = x_entities_all.copy()

to_remove = filter(lambda x: len(x) < 4, list(x_entities_all.keys()))
for i in list(to_remove):
    x_entities.pop(i)
    

# Character Superpower
char_sp = []

for x_key, x_val in x_entities.items():
    c_s = pd.DataFrame({"char_id": x_key, "superpoder_id": get_id(x_val, super_power)})
    char_sp.append(c_s)          
                     
char_sp_df = pd.concat(char_sp)
char_sp_df.to_csv("char_sp.csv", encoding="utf-8", index=False)


super_power_list = []
gender_list = []
teams_list = []
universe_list = []

for i in x_entities.values():
    super_power_list.append(get_id(i, super_power))
    gender_list.append(get_id(i, gender))
    teams_list.append(get_id(i, teams))
    universe_list.append(get_id(i, universe))

sp_unique, gn_unique, tm_unique, un_unique = [
    get_unique(i) for i in [super_power_list, gender_list, teams_list, universe_list]
    ]

gn_df = pd.DataFrame(props_dict(gn_unique))
un_df = pd.DataFrame(props_dict(un_unique))
sp_df = pd.DataFrame(props_dict(sp_unique))
tm_df = pd.DataFrame(props_dict(tm_unique))

gn_df.to_csv("genders.csv", encoding="utf-8", index=False)
un_df.to_csv("universes.csv", encoding="utf-8", index=False)
sp_df.to_csv("superpowers.csv", encoding="utf-8", index=False)
tm_df.to_csv("teams.csv", encoding="utf-8", index=False)