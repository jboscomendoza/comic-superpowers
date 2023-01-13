import streamlit as st
import pandas as pd
from plotly import graph_objects as go

cols_str = ["char_desc", "sp_nombre", "sp_desc", "team_desc", "gen_nombre"]

ESWIKI_URL = "https://es.wikipedia.org/wiki/"


def crear_enlace(wiki_link):
    if wiki_link == "" or wiki_link is None:
        wiki_link_txt = u"No tiene articulo en Wikipedia."
    else:
        wiki_link = wiki_link.replace(" ", "_")
        wiki_link = ESWIKI_URL+wiki_link
        wiki_link_txt = u"[Artículo en Wikipedia]({})".format(wiki_link)
    return wiki_link_txt


char = pd.read_parquet("char_data.parquet")
char = char.rename(columns={"char_eswiki": "char_wiki"})

char[cols_str] = char[cols_str].apply(lambda x: x.str.capitalize())


char_unique = char["char_nombre"].unique()

conteo_sp = (
    char[["char_nombre", "sp_nombre"]]
    .drop_duplicates()
    .groupby("sp_nombre", as_index=False)
    .count()
    .sort_values("char_nombre", ascending=False)
    .reset_index(drop=True)
)
conteo_sp.columns = ["Superpoder", "Conteo"]

conteo_team = (
    char[["char_nombre", "team_nombre"]]
    .drop_duplicates()
    .groupby("team_nombre", as_index=False)
    .count()
    .sort_values("char_nombre", ascending=False)
    .reset_index(drop=True)
)
conteo_team.columns = ["Equipo", "Conteo"]

conteos = {
    "Personajes": len(char_unique), 
    "Poderes": len(conteo_sp),
    "Equipos": len (conteo_team)
}


### ###
### App
### ###
st.markdown("# X-Men")

metric_cols = st.columns(len(conteos))

for cont_k, cont_v, cont_col in zip(conteos.keys(), conteos.values(), metric_cols):
    cont_col.metric(cont_k, cont_v)


# Tabs
tab_sp, tab_team, tab_char = st.tabs([
    ":mortar_board: Poderes", 
    ":globe_with_meridians: Equipos", 
    ":busts_in_silhouette: Personajes"])

## Poder
sp_bar = go.Figure()
sp_bar.add_trace(go.Bar(   
    x=conteo_sp["Superpoder"].str.slice(0, 20),
    y=conteo_sp["Conteo"]
))
sp_bar.update_layout(dict(
     height=300, 
     margin=dict(t=25, r=0, b=0, l=0),
     ))

tab_sp.markdown("## Poderes más frecuentes")
tab_sp.plotly_chart(sp_bar)

sel_sp = tab_sp.selectbox("Elige un poder", char["sp_nombre"].sort_values().unique())

sp_desc = char["sp_desc"].loc[char["sp_nombre"] == sel_sp].unique().item()
tab_sp.markdown(sp_desc+".")

sp_wiki = char["sp_wiki"].loc[char["sp_nombre"] == sel_sp].unique().item()
tab_sp.markdown(crear_enlace(sp_wiki))

char_sp = char["char_nombre"].loc[char["sp_nombre"] == sel_sp].drop_duplicates()
tab_sp.metric("Personajes con este poder", len(char_sp))
char_sp_nombres = (
    char_sp
    .to_frame()
    .sort_values("char_nombre")
    .reset_index(drop=True)
    .rename(columns={"char_nombre":"Personaje"})
    )
tab_sp.table(char_sp_nombres)


## Equipos
team_bar = go.Figure()
team_bar.add_trace(go.Bar(   
    x=conteo_team["Equipo"].str.slice(0, 20),
    y=conteo_team["Conteo"]
))
team_bar.update_layout(dict(
     height=300, 
     margin=dict(t=25, r=0, b=0, l=0),
     ))


tab_team.markdown("## Equipos más frecuentes")
tab_team.plotly_chart(team_bar)


sel_team = tab_team.selectbox("Elige un equipo", char["team_nombre"].sort_values().unique())

team_desc = char["team_desc"].loc[char["team_nombre"] == sel_team].unique().item()
tab_team.markdown(team_desc+".")

char_team = char["char_nombre"].loc[char["team_nombre"] == sel_team].drop_duplicates()
team_wiki = char["team_wiki"].loc[char["team_nombre"] == sel_team].unique().item()

tab_team.markdown(crear_enlace(team_wiki))
tab_team.metric("Personajes que han sido integrantes de este equipo", len(char_team))
char_team_nombres = (
    char_team
    .to_frame()
    .sort_values("char_nombre")
    .reset_index(drop=True)
    .rename(columns={"char_nombre":"Personaje"})
    )
tab_team.table(char_team_nombres)


# Personajes
conteo_gen = char[["char_nombre", "gen_nombre"]].drop_duplicates().groupby("gen_nombre", as_index=False).count()
gen_bar = go.Figure()
gen_bar.add_trace(go.Bar(   
    x=conteo_gen["gen_nombre"],
    y=conteo_gen["char_nombre"]
))
gen_bar.update_layout(dict(
     height=200, 
     margin=dict(t=25, r=0, b=0, l=0),
     ))


tab_char.plotly_chart(gen_bar)

sel_char = tab_char.selectbox(
    "Elige un personaje",
    char["char_nombre"].unique()
)

pers = char.loc[char["char_nombre"] == sel_char]

char_desc = pers["char_desc"].unique().item()

char_wiki = pers["char_wiki"].unique().item()
if char_wiki == "" :
    char_wiki_txt = u"No tiene articulo en Wikipedia."
else:
    char_wiki = char_wiki.replace(" ", "_")
    char_wiki = ESWIKI_URL+char_wiki
    char_wiki_txt = u"[Artículo en Wikipedia]({})".format(char_wiki)

tab_char.markdown(char_desc+".")
tab_char.markdown(char_wiki_txt)



contenido = {
    u"Género": pers["gen_nombre"].drop_duplicates(),
    "Poderes": pers["sp_nombre"].drop_duplicates(),
    "Equipos": pers["team_nombre"].drop_duplicates(),
    "Universos": pers["uni_nombre"].drop_duplicates()
}
char_cols = tab_char.columns(len(contenido))

for i_col, i_key, i_value in zip(char_cols, contenido.keys(), contenido.values()):
    i_col.markdown("### "+i_key)
    for value_in_v in i_value:
        i_col.markdown(value_in_v)