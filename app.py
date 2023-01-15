import streamlit as st
import pandas as pd
from plotly import graph_objects as go

st.set_page_config(
    page_title="X-Men poderes",
    page_icon=":book:",
    layout="centered",
    initial_sidebar_state="expanded"
)

COLS_STR = ["char_desc", "sp_nombre", "sp_desc", "team_desc", "gen_nombre"]
ESWIKI_URL = "https://es.wikipedia.org/wiki/"


def crear_enlace(wiki_link):
    if wiki_link == "Faltante" or wiki_link is None:
        wiki_link_txt = u"No tiene articulo en Wikipedia."
    else:
        wiki_link = wiki_link.replace(" ", "_")
        wiki_link = ESWIKI_URL+wiki_link
        wiki_link_txt = u"[Artículo en Wikipedia]({})".format(wiki_link)
    return wiki_link_txt


def crear_descripcion(tipo, s_tab, seleccion):
    mensaje = {
        "team": "Personajes que han sido integrantes de este equipo.",
        "sp":   "Personajes con este poder.",
        "uni":  "Personajes que habitan este universo."
    } 
    s_desc = char[tipo+"_desc"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_tab.markdown(s_desc+".")
    s_wiki = char[tipo+"_wiki"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_char = char["char_nombre"].loc[char[tipo+"_nombre"] == seleccion].drop_duplicates()
    s_tab.markdown(crear_enlace(s_wiki))
    s_tab.metric(mensaje[tipo], s_char.count())
    s_char_nombres = (
        s_char
        .to_frame()
        .sort_values("char_nombre")
        .reset_index(drop=True)
        .rename(columns={"char_nombre":"Personaje"})
    )
    s_tab.table(s_char_nombres)


# Data
char = pd.read_parquet("char_data.parquet")
char = char.rename(columns={"char_eswiki": "char_wiki"})
char[COLS_STR] = char[COLS_STR].apply(lambda x: x.str.capitalize())
char = char.fillna("Faltante")
char = char.replace({"": "Faltante"})


# Conteos
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

conteo_gen = (
    char[["char_nombre", "gen_nombre"]]
    .drop_duplicates()
    .groupby("gen_nombre", as_index=False)
    .count()
)

# Plots
layout_dict = dict(
    height=300, 
    margin=dict(t=25, r=0, b=0, l=0)
    )

sp_bar = go.Figure()
sp_bar.add_trace(go.Bar(   
    x=conteo_sp["Superpoder"].str.slice(0, 20),
    y=conteo_sp["Conteo"]
))
sp_bar.update_layout(layout_dict)

team_bar = go.Figure()
team_bar.add_trace(go.Bar(   
    x=conteo_team["Equipo"].str.slice(0, 20),
    y=conteo_team["Conteo"]
))
team_bar.update_layout(layout_dict)

gen_bar = go.Figure()
gen_bar.add_trace(go.Bar(   
    x=conteo_gen["gen_nombre"],
    y=conteo_gen["char_nombre"]
))
gen_bar.update_layout(layout_dict)

### ###
### App
### ###
st.markdown("# X-Men")

metric_cols = st.columns(len(conteos))

for cont_k, cont_v, cont_col in zip(conteos.keys(), conteos.values(), metric_cols):
    cont_col.metric(cont_k, cont_v)


## Tabs
tab_char, tab_sp, tab_team = st.tabs([
    ":busts_in_silhouette: Personajes",
    ":mortar_board: Poderes", 
    ":globe_with_meridians: Equipos", 
    ])


# Personajes
tab_char.plotly_chart(gen_bar)

char_sel = tab_char.selectbox(
    "Elige un personaje",
    char["char_nombre"].unique()
)

pers = char.loc[char["char_nombre"] == char_sel]

char_desc = pers["char_desc"].unique().item()

char_wiki = pers["char_wiki"].unique().item()

tab_char.markdown(char_desc+".")
tab_char.markdown(crear_enlace(char_wiki))

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


## Poder
tab_sp.markdown("## Poderes más frecuentes")
tab_sp.plotly_chart(sp_bar)

sp_sel = tab_sp.selectbox("Elige un poder", char["sp_nombre"].sort_values().unique())

crear_descripcion("sp", tab_sp, sp_sel)

## Equipos
tab_team.markdown("## Equipos más frecuentes")

tab_team.plotly_chart(team_bar)

team_sel = tab_team.selectbox("Elige un equipo", char["team_nombre"].sort_values().unique())

crear_descripcion("team", tab_team, team_sel)