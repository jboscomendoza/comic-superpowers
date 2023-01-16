import streamlit as st
import pandas as pd
import graph_plots as gp
import matplotlib.pyplot as plt
from plotly import graph_objects as go

st.set_page_config(
    page_title="X-Men poderes",
    page_icon=":book:",
    layout="centered",
    initial_sidebar_state="expanded"
)

COLS_STR = ["char_desc", "sp_nombre", "sp_desc", "team_desc", "gen_nombre", "uni_desc"]
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
        "team": "Personajes que han sido integrantes de este equipo",
        "sp":   "Personajes con este poder",
        "uni":  "Personajes que habitan este universo"
    } 
    s_desc = char[tipo+"_desc"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_tab.markdown(s_desc+".")
    s_wiki = char[tipo+"_wiki"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_char = char["char_nombre"].loc[char[tipo+"_nombre"] == seleccion].drop_duplicates()
    s_tab.markdown(crear_enlace(s_wiki))
    
    s_tab.markdown("## "+mensaje[tipo])
    s_col1, s_col2 = s_tab.columns([1, 4])
    s_col1.metric(label="Total de personajes", value=s_char.count())
    s_char_nombres = (
        s_char
        .to_frame()
        .sort_values("char_nombre")
        .reset_index(drop=True)
        .rename(columns={"char_nombre":"Personaje"})
    )
    s_col2.dataframe(s_char_nombres, use_container_width=True)


def get_faltantes(tipo, datos):
    tipo_cols = [f"{tipo}_nombre", f"{tipo}_wiki", f"{tipo}_desc"]
    tipo_names = ["Nombre", "Wiki", u"Descripción"]
    if tipo == "char":
        tipo_cols.append("sp_nombre")
        tipo_names.append("Poderes")
    tipo_data = datos[tipo_cols]
    tipo_data = tipo_data.loc[tipo_data[f"{tipo}_nombre"]!="Faltante"]
    tipo_sel = tipo_data.loc[tipo_data.isin(["Faltante"]).any(axis=1)]
    tipo_sel = tipo_sel.drop_duplicates().reset_index(drop=True)
    tipo_sel.columns = tipo_names
    return tipo_sel


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
char_tab, sp_tab, team_tab, fal_tab = st.tabs([
    ":busts_in_silhouette: Personajes",
    ":mortar_board: Poderes", 
    ":globe_with_meridians: Equipos", 
    ":construction: Faltantes"
    ])


# Personajes
char_tab.markdown("## Elige un personaje")
char_sel = char_tab.selectbox(
    " personaje",
    options=char["char_nombre"].unique(),
    label_visibility="collapsed"
)

pers = char.loc[char["char_nombre"] == char_sel]

char_desc = pers["char_desc"].unique().item()

char_wiki = pers["char_wiki"].unique().item()

char_tab.markdown(u"## Descripción")
char_tab.markdown(char_desc+".")
char_tab.markdown(crear_enlace(char_wiki))

contenido = {
    u"Género": pers["gen_nombre"].drop_duplicates(),
    "Poderes": pers["sp_nombre"].drop_duplicates(),
    "Equipos": pers["team_nombre"].drop_duplicates(),
    "Universos": pers["uni_nombre"].drop_duplicates()
}

char_cols = char_tab.columns(len(contenido))

for i_col, i_key, i_value in zip(char_cols, contenido.keys(), contenido.values()):
    i_col.markdown("### "+i_key)
    for value_in_v in i_value:
        i_col.markdown(value_in_v)

char_tab.markdown(u"## Personajes por género")
char_tab.plotly_chart(gen_bar)


## Poder
sp_tab.markdown("## Poderes más frecuentes")
sp_tab.plotly_chart(sp_bar)

sp_tab.markdown("## Elige un poder")
sp_sel = sp_tab.selectbox(
    "Elige un poder", 
    options=char["sp_nombre"].sort_values().unique(),
    label_visibility="collapsed")

sp_tab.markdown("## Descripción")
crear_descripcion("sp", sp_tab, sp_sel)

sp_fig, sp_ax = plt.subplots()
sp_ax.set_frame_on(False)
gp.graph_sp(sp_sel, char)
sp_tab.markdown(u"## Relación entre poderes")
sp_tab.pyplot(sp_fig, facecolor="#0e1117")

## Equipos
team_tab.markdown(u"## Equipos con más integrantes")
team_tab.plotly_chart(team_bar)

team_tab.markdown("## Elige un equipo")
team_sel = team_tab.selectbox(
    "Elige un equipo", 
    options=char["team_nombre"].sort_values().unique(),
    label_visibility="collapsed"
    )

team_tab.markdown(u"## Descripción")
crear_descripcion("team", team_tab, team_sel)

team_fig, team_ax = plt.subplots()
team_ax.set_frame_on(False)
gp.graph_team(team_sel, char)
team_tab.markdown(u"## Relación entre equipos")
team_tab.pyplot(team_fig, facecolor="#0e1117")


## Faltantes
fal_tab.markdown("## Entradas con datos faltantes")

fal_sel = fal_tab.selectbox(
    "Elige un tipo de entrada", 
    ["Personajes", "Poderes", "Equipos", "Universos"]
)

fal_dict = {
    "Personajes": "char",
     "Poderes": "sp",
     "Equipos": "team",
     "Universos": "uni"
     }

fal_tab.dataframe(
    get_faltantes(fal_dict[fal_sel], datos=char),
    use_container_width=True
    )