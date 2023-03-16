import time
import reqchars as rc
import pandas as pd
import numpy as np

# Funciones de ayuda
def get_unique(info_list):
    unique_list = [ip for i_list in info_list for ip in i_list]
    unique_list = set(unique_list)
    unique_list = list(filter(lambda x: x is not None, unique_list))
    return unique_list


# Identificadores en wikidata
SUPER_POWER = "P2563"
GENDER      = "P21"
TEAMS       = "P463"
UNIVERSE    = "P1080"
CREATORS    = "P170"


# Lectura de nombres de chars
with open("scrape\wiki_links.txt", "r") as links_file:
    x_men = links_file.readlines()
    x_men = [i.rstrip("\n") for i in x_men]

x_men_groups = rc.dividir_grupos(x_men, 25)


# Listado de atributos
x_men_ents   = []
num_consulta = 1

for x_men_names in x_men_groups:
    entity_group = rc.get_entity(x_men_names, type="title")
    x_men_ents.append(entity_group)
    # Pausa de cortesia
    print(f"Consulta {num_consulta}")
    num_consulta+=1
    time.sleep(1.5)
    

# Entidades a lista desagrupada, en lugar de agrupada
x_entities_all = dict()

for i in x_men_ents:
    x_entities_all.update(i["entities"])

x_entities = x_entities_all.copy()


# Filtra entidades que no tienen entrada en wikidata, identificado
# por un diccionaro con menos de 4 keys, el largo esperado
to_remove = filter(lambda x: len(x) < 4, list(x_entities_all.keys()))

for i in list(to_remove):
    x_entities.pop(i)


# Character info
# dataframe: char_id; char_nombre; char_desc; gen_id; char_wiki
char_info = []

for id_ent, datos_ent in x_entities.items():
    c_info = {
        "char_id": id_ent,
        "char_nombre": datos_ent.get("labels", {}).get("es", {}).get("value", ""),
        "char_desc": datos_ent.get("descriptions", {}).get("es", {}).get("value", ""),
        "gen_id": rc.get_id(datos_ent, GENDER)[0],
        "char_wiki": datos_ent.get("sitelinks", {}).get("eswiki", {}).get("title", "")
    }
    char_info.append(c_info)

char_info_df = pd.DataFrame(char_info)


# Character superpowers
char_sp = []
for x_key, x_val in x_entities.items():
    c_s = pd.DataFrame({"char_id": x_key, "sp_id": rc.get_id(x_val, SUPER_POWER)})
    char_sp.append(c_s)
char_sp_df = pd.concat(char_sp)


# Character TEAMS
char_team = []
for x_key, x_val in x_entities.items():
    c_t = pd.DataFrame({"char_id": x_key, "team_id": rc.get_id(x_val, TEAMS)})
    char_team.append(c_t)
char_team_df = pd.concat(char_team)


# Character UNIVERSE
char_universe = []
for x_key, x_val in x_entities.items():
    c_u = pd.DataFrame({"char_id": x_key, "uni_id": rc.get_id(x_val, UNIVERSE)})
    char_universe.append(c_u)
char_universe_df = pd.concat(char_universe)


# Chracter creator
char_creator = []
for x_key, x_val in x_entities.items():
    c_c = pd.DataFrame({"char_id": x_key, "crea_id": rc.get_id(x_val, CREATORS)})
    char_creator.append(c_c)
char_creator_df = pd.concat(char_creator)


# Listas de atributos únicos
super_power_list = []
gender_list      = []
teams_list       = []
universe_list    = []
creator_list     = []

for i in x_entities.values():
    super_power_list.append(rc.get_id(i, SUPER_POWER))
    gender_list.append(rc.get_id(i, GENDER))
    teams_list.append(rc.get_id(i, TEAMS))
    universe_list.append(rc.get_id(i, UNIVERSE))
    creator_list.append(rc.get_id(i, CREATORS))

sp_unique, gn_unique, tm_unique, un_unique, cr_unique = [
    get_unique(i) for i in [super_power_list, gender_list, 
                            teams_list, universe_list, creator_list]
    ]


# Dataframes con valores para cada atributo
gn_df = pd.DataFrame(rc.props_dict(gn_unique, "gen"))
sp_df = pd.DataFrame(rc.props_dict(sp_unique, "sp"))
un_df = pd.DataFrame(rc.props_dict(un_unique, "uni"))
tm_df = pd.DataFrame(rc.props_dict(tm_unique, "team"))
cr_df = pd.DataFrame(rc.props_dict(cr_unique, "crea"))


# Dataframes integrados
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


# Esportar a parquet, requiere pyarrow
char_data.to_parquet("data/char_data.parquet", index=False)


# Exportar a csv
gn_df.to_csv("data/genders.csv", encoding="utf-8", index=False)
un_df.to_csv("data/universes.csv", encoding="utf-8", index=False)
sp_df.to_csv("data/superpowers.csv", encoding="utf-8", index=False)
tm_df.to_csv("data/teams.csv", encoding="utf-8", index=False)
cr_df.to_csv("data/creators.csv", encoding="utf-8", index=False)
# char_sp_df.to_csv("char_sp.csv", encoding="utf-8", index=False)
# char_team_df.to_csv("char_team.csv", encoding="utf-8", index=False)
# char_info_df.to_csv("char_info.csv", encoding="utf-8", index=False)
# char_universe_df.to_csv("char_universe.csv", encoding="utf-8", index=False)