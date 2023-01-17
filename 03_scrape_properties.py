import time
import reqchars as rc
import pandas as pd
import numpy as np


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


def props_dict(lista_unicos, prefix):
    unique_list = []
    grupos = dividir_grupos(lista_unicos)
    for grp in grupos:
        unique_ents = rc.get_entity(grp, "id")
        for i in lista_unicos:
            props = unique_ents.get("entities").get(i)
            if props is not None:
                ent_props = {
                    prefix+"_id": props.get("id"),
                    prefix+"_nombre": props.get("labels").get("es", {}).get("value"),
                    prefix+"_desc": props.get("descriptions", {}).get("es", {}).get("value"),
                    prefix+"_idioma": props.get("descriptions", {}).get("es", {}).get("language"),
                    prefix+"_wiki": props.get("sitelinks", {}).get("eswiki", {}).get("title")
                }
                unique_list.append(ent_props)
    return unique_list


super_power = "P2563"
gender = "P21"
teams = "P463"
universe = "P1080"
creators = "P170"


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

# Filtra entidades que no tienen entrada en wikidata, identificado
# por un diccionaro con menos keys
to_remove = filter(lambda x: len(x) < 4, list(x_entities_all.keys()))
for i in list(to_remove):
    x_entities.pop(i)


# Character info
# dataframe: char_id; char_nombre; char_desc; gen_id; char_wiki
char_info = []
for x_key, x_val in x_entities.items():
    c_info = {
        "char_id": x_key,
        "char_nombre": x_val.get("labels", {}).get("es", {}).get("value", ""),
        "char_desc": x_val.get("descriptions", {}).get("es", {}).get("value", ""),
        "gen_id": get_id(x_val, gender)[0],
        "char_wiki": x_val.get("sitelinks", {}).get("eswiki", {}).get("title", "")
    }
    char_info.append(c_info)
char_info_df = pd.DataFrame(char_info)

# Character superpowers
char_sp = []
for x_key, x_val in x_entities.items():
    c_s = pd.DataFrame({"char_id": x_key, "sp_id": get_id(x_val, super_power)})
    char_sp.append(c_s)
char_sp_df = pd.concat(char_sp)

# Character teams
char_team = []
for x_key, x_val in x_entities.items():
    c_t = pd.DataFrame({"char_id": x_key, "team_id": get_id(x_val, teams)})
    char_team.append(c_t)
char_team_df = pd.concat(char_team)

# Character universe
char_universe = []
for x_key, x_val in x_entities.items():
    c_u = pd.DataFrame({"char_id": x_key, "uni_id": get_id(x_val, universe)})
    char_universe.append(c_u)
char_universe_df = pd.concat(char_universe)

# Chracter creator
char_creator = []
for x_key, x_val in x_entities.items():
    c_c = pd.DataFrame({"char_id": x_key, "crea_id": get_id(x_val, creators)})
    char_creator.append(c_c)
char_creator_df = pd.concat(char_creator)

# Properties
super_power_list = []
gender_list = []
teams_list = []
universe_list = []
creator_list = []

for i in x_entities.values():
    super_power_list.append(get_id(i, super_power))
    gender_list.append(get_id(i, gender))
    teams_list.append(get_id(i, teams))
    universe_list.append(get_id(i, universe))
    creator_list.append(get_id(i, creators))

sp_unique, gn_unique, tm_unique, un_unique, cr_unique = [
    get_unique(i) for i in [super_power_list, gender_list, 
                            teams_list, universe_list, creator_list]
    ]

gn_df = pd.DataFrame(props_dict(gn_unique, "gen"))
sp_df = pd.DataFrame(props_dict(sp_unique, "sp"))
un_df = pd.DataFrame(props_dict(un_unique, "uni"))
tm_df = pd.DataFrame(props_dict(tm_unique, "team"))
cr_df = pd.DataFrame(props_dict(cr_unique, "crea"))

char_data = pd.merge(char_info_df, char_sp_df, on="char_id", how="left")
char_data = pd.merge(char_data, char_team_df, on="char_id", how="left")
char_data = pd.merge(char_data, char_universe_df, on="char_id", how="left")
char_data = pd.merge(char_data, char_creator_df, on="char_id", how="left")
char_data = pd.merge(char_data, gn_df, on="gen_id", how="left")
char_data = pd.merge(char_data, sp_df, on="sp_id", how="left")
char_data = pd.merge(char_data, tm_df, on="team_id", how="left")
char_data = pd.merge(char_data, un_df, on="uni_id", how="left")
char_data = pd.merge(char_data, cr_df, on="crea_id", how="left")
char_data = char_data.replace({"None":np.nan, None:np.nan})

# Requires pyarrow
char_data.to_parquet("char_data.parquet", index=False)

gn_df.to_csv("genders.csv", encoding="utf-8", index=False)
un_df.to_csv("universes.csv", encoding="utf-8", index=False)
sp_df.to_csv("superpowers.csv", encoding="utf-8", index=False)
tm_df.to_csv("teams.csv", encoding="utf-8", index=False)
cr_df.to_csv("creators.csv", encoding="utf-8", index=False)
# char_sp_df.to_csv("char_sp.csv", encoding="utf-8", index=False)
# char_team_df.to_csv("char_team.csv", encoding="utf-8", index=False)
# char_info_df.to_csv("char_info.csv", encoding="utf-8", index=False)
# char_universe_df.to_csv("char_universe.csv", encoding="utf-8", index=False)