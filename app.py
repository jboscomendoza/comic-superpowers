import streamlit as st
import pandas as pd
import numpy as np
import graph_plots as gp
from plotly import graph_objects as go
import streamlit.components.v1 as components


st.set_page_config(
    page_title="X-Men Wikidatos",
    page_icon=":book:",
    layout="centered",
    initial_sidebar_state="expanded"
)


def get_conteo(ent_tipo:str, datos:pd.DataFrame) -> pd.DataFrame:
    """ent_tipo uno de sp, team, gen, crea, uni"""
    ent_dict = {
        "sp":   u"Superpoder",
        "team": "Equipo",
        "gen":  u"Género",
        "crea": "Creador",
        "uni":  "Universo"
    }
    nombre = ent_tipo+"_nombre" 
    conteo = (
        datos[["char_nombre", nombre]]
        .loc[datos[nombre] != "Faltante"]
        .drop_duplicates()
        .value_counts(subset=nombre, ascending=False)
        .to_frame()
        .reset_index()
        .rename(columns={nombre: ent_dict[ent_tipo], 0:"Conteo"})
    )
    return conteo


def contar_como_otros(conteo:pd.DataFrame, frecuencia:int) -> pd.DataFrame:
    """conteo: dataframe con conteos; frecuencia: cualquiera mayor a 1"""
    col_main = conteo.columns[0]
    conteo[col_main] = np.where(conteo["Conteo"]<frecuencia, 
                                "Otros", 
                                conteo[col_main])
    conteo = (
        conteo
        .groupby(col_main, as_index=False)
        .sum()
        .sort_values("Conteo", ascending=False)
        )
    return conteo


def get_bars(conteo, alto=300):
    tick_labs = []

    x_values = conteo.iloc[:, 0]
    y_values = conteo.iloc[:, 1]
    for i in x_values:
        if len(i) > 18:
            lab = i[0:18] + u"…"
            tick_labs.append(lab)
        else:
            tick_labs.append(i)
    bars = go.Figure()
    bars.add_trace(go.Bar(
        name=conteo.columns[0],
        x=x_values,
        y=y_values,
        text=x_values,
        textposition="none",
        hovertemplate="%{text}: %{y}"
    ))
    bars.update_layout(
        height=alto, 
        margin=dict(t=25, r=0, b=0, l=0),
        xaxis = dict(
            tickmode="array",
            tickvals=x_values,
            ticktext=tick_labs
            )
    )
    return bars


def crear_enlace(wiki_link, wiki_tipo):
    """Tipo: Uno de eswiki o wikidata"""
    wiki_link = str(wiki_link)
    wiki_link = wiki_link.replace(" ", "_")
    sitio_dict = {
        "eswiki": {
            "sitio":u"Wikipedia en español",
            "url": "https://es.wikipedia.org/wiki/"
            },
        "wikidata": {
            "sitio":"Wikidata",
            "url":"https://www.wikidata.org/wiki/"
            }
        }
    
    sitio = sitio_dict[wiki_tipo]["sitio"]
    sitio_url = sitio_dict[wiki_tipo]["url"]+wiki_link
    
    if wiki_link in ["Faltante", "None"]:
        return u"No tiene articulo en "+sitio
    return f"[{sitio}]({sitio_url})"


def get_unique(columna:pd.Series) -> list:
    """Valores únicos de una columna, sin valor 'Faltante'"""
    col_unique = (
        columna
        .loc[columna!="Faltante"]
        .sort_values()
        .unique()
    )
    return list(col_unique)


def crear_descripcion(tipo:str, s_tab:st.tabs, seleccion:str, datos:pd.DataFrame):
    mensaje = {
        "char": "Personaje",
        "team": "Personajes que han sido integrantes de este equipo",
        "sp":   "Personajes con este poder",
        "uni":  "Personajes que habitan este universo",
        "crea": "Personajes creados por esta persona",
    } 
    s_tab.markdown(u"### Descripción")
    s_desc = datos[tipo+"_desc"].loc[datos[tipo+"_nombre"] == seleccion].unique().item()
    s_tab.markdown(s_desc+".")
    s_wiki = datos[tipo+"_wiki"].loc[datos[tipo+"_nombre"] == seleccion].unique().item()
    s_id = datos[tipo+"_id"].loc[datos[tipo+"_nombre"] == seleccion].unique().item()
    s_char = datos["char_nombre"].loc[datos[tipo+"_nombre"] == seleccion].drop_duplicates()
    
    enlace_eswiki   = crear_enlace(s_wiki, "eswiki")
    enlace_wikidata = crear_enlace(s_id, "wikidata")
    s_tab.markdown(f"[ {enlace_eswiki} - {enlace_wikidata} ]")
    
    if tipo != "char":
        s_tab.markdown("### "+mensaje[tipo])
        s_col1, s_col2 = s_tab.columns([1, 4])
        s_col1.metric(label="Total de personajes", value=s_char.count())
        s_char_nombres = (
            s_char
            .to_frame()
            .sort_values("char_nombre")
            .reset_index(drop=True)
            .rename(columns={"char_nombre":"Personaje"})
        )
        
        char_to_show = (
            datos
            .loc[datos["char_nombre"].isin(s_char_nombres["Personaje"])]
            [["char_nombre", "char_wiki", "char_id"]]
            .drop_duplicates()
        )
        
        # Lista colapsable de personajes
        with s_col2.expander("Ver personajes"):
            for index, row in char_to_show.iterrows():
                char_nombre = row["char_nombre"]
                char_wiki   = crear_enlace(row["char_wiki"], "eswiki")
                char_data   = crear_enlace(row["char_id"], "wikidata")
                st.markdown(f"{char_nombre} [ {char_wiki} - {char_data} ]")


def get_faltantes(tipo:str, datos:pd.DataFrame) -> pd.DataFrame:
    """tipo: uni de char, sp, tram, uni, crea"""
    # Columnas en las que se buscaran faltantes
    tipo_cols = [f"{tipo}_nombre", f"{tipo}_wiki", f"{tipo}_desc"]
    tipo_names = ["Nombre", "Wiki", u"Descripción"]
    # Columnas adicionales para personajes
    if tipo == "char":
        tipo_cols.append("sp_nombre") 
        tipo_cols.append("crea_nombre")
        tipo_names.append("Poderes")
        tipo_names.append("Creador")
    tipo_data = datos[tipo_cols]
    tipo_data = tipo_data.loc[tipo_data[f"{tipo}_nombre"]!="Faltante"]
    tipo_sel = tipo_data.loc[tipo_data.isin(["Faltante"]).any(axis=1)]
    tipo_sel = tipo_sel.drop_duplicates().reset_index(drop=True)
    tipo_sel.columns = tipo_names
    return tipo_sel


# Data
char = pd.read_parquet("data/char_data.parquet")
char = char.fillna("Faltante")
char = char.replace({"": "Faltante"})
str_cols = ["sp_nombre", "gen_nombre", 
            "sp_desc", "char_desc", "team_desc", "gen_desc", "crea_desc"]
char[str_cols] = char[str_cols].apply(lambda x: x.str.capitalize())


### ###
### App
### ###
st.markdown("# X-Men - Wikidatos")
bg_style ="" "<style>:root {background-color:#0e1117; padding:10px;}</style>"

## Tabs
char_tab, sp_tab, team_tab, crea_tab, bar_tab, fal_tab = st.tabs([
    ":busts_in_silhouette: Personajes",
    ":mortar_board: Poderes", 
    ":globe_with_meridians: Equipos",
    ":brain: Creadores",
    ":bar_chart: Resumen",
    ":construction: Faltantes"
    ])


## Personajes
char_tab.markdown("### Elige un personaje")
char_sel = char_tab.selectbox(
    " personaje",
    options=char["char_nombre"].unique(),
    label_visibility="collapsed"
)

pers = char.loc[char["char_nombre"] == char_sel]

char_desc = pers["char_desc"].unique().item()

char_wiki = pers["char_wiki"].unique().item()
char_wiki = pers["char_id"].unique().item()

crear_descripcion("char", char_tab, char_sel, char)

contenido = {
    u"Género": pers["gen_nombre"].drop_duplicates(),
    "Poderes": pers["sp_nombre"].drop_duplicates(),
    "Equipos": pers["team_nombre"].drop_duplicates(),
    "Universos": pers["uni_nombre"].drop_duplicates(),
    "Creadores": pers["crea_nombre"].drop_duplicates()
}

char_cols = char_tab.columns(len(contenido))

for i_col, i_key, i_value in zip(char_cols, contenido.keys(), contenido.values()):
    i_col.markdown("### "+i_key)
    for value_in_v in i_value:
        i_col.markdown(value_in_v)


## Poder
sp_tab.markdown("### Elige un poder")
sp_sel = sp_tab.selectbox(
    "Elige un poder", 
    options=get_unique(char["sp_nombre"]),
    label_visibility="collapsed")

crear_descripcion("sp", sp_tab, sp_sel, char)

sp_tab.markdown(u"### Relación entre poderes")
gp.graph_pairs(sp_sel, "sp", char)
sp_html = open("sp.html",'r',encoding='utf-8')
with sp_tab:
    components.html(bg_style+sp_html.read(), height=475)


## Equipos
team_tab.markdown("## Elige un equipo")
team_sel = team_tab.selectbox(
    "Elige un equipo", 
    options=get_unique(char["team_nombre"]),
    label_visibility="collapsed"
    )

crear_descripcion("team", team_tab, team_sel, char)

team_tab.markdown(u"### Relación entre equipos")

gp.graph_team(team_sel, char)
team_html = open("teams.html",'r',encoding='utf-8')
with team_tab:
    components.html(bg_style+team_html.read(), height=475)


## Creadores
crea_tab.markdown("### Elige un creador")
crea_sel = crea_tab.selectbox(
    "Elige un creador", 
    options=get_unique(char["crea_nombre"]),
    label_visibility="collapsed"
    )

crear_descripcion("crea", crea_tab, crea_sel, char)

crea_tab.markdown(u"### Colaboración entre creadores")
gp.graph_pairs(crea_sel, "crea", char)
crea_html = open("crea.html",'r',encoding='utf-8')
with crea_tab:
    components.html(bg_style+crea_html.read(), height=475)


## Resumen
# Elementos resumen
sp_conteo, team_conteo, crea_conteo, gen_conteo = [get_conteo(i, char) for i in [
    "sp", "team", "crea", "gen"]]

totales = {
    "Personajes": len(char["char_nombre"].unique()),
    "Poderes": len(sp_conteo),
    "Equipos": len (team_conteo),
    "Creadores": len (crea_conteo)
}


bar_tab.markdown(u"### Totales")
metric_cols = bar_tab.columns(len(totales))
for cont_k, cont_v, cont_col in zip(totales.keys(), totales.values(), metric_cols):
    cont_col.metric(cont_k, cont_v)

bar_tab.markdown(u"### Personajes por género")
bar_tab.plotly_chart(get_bars(gen_conteo, 200))

bar_tab.markdown(u"### Tipo de agrupamiento")

bar_col1, bar_col2 = bar_tab.columns([2, 1])
como_otros = bar_col1.checkbox("Agrupar como 'Otros' elementos con frecuencia menor a:")
frecuencia = bar_col2.number_input('Frecuencia', 
                                  min_value=2, max_value=10, step=1, 
                                  label_visibility="collapsed")

if como_otros:
    sp_conteo, team_conteo, crea_conteo = [contar_como_otros(i, frecuencia) for i in [
        sp_conteo, team_conteo, crea_conteo]]

sp_bar, team_bar, crea_bar = [get_bars(i) for i in [
    sp_conteo, team_conteo, crea_conteo]]

bar_tab.markdown("### Poderes más frecuentes")
bar_tab.plotly_chart(sp_bar)

bar_tab.markdown(u"### Equipos con más integrantes")
bar_tab.plotly_chart(team_bar)

bar_tab.markdown(u"### Personajes por creador")
bar_tab.plotly_chart(crea_bar)


## Faltantes
fal_tab.markdown("### Entradas con datos faltantes")

fal_sel = fal_tab.selectbox(
    "Elige un tipo de entrada", 
    ["Personajes", "Poderes", "Equipos", "Universos", "Creadores"]
)

fal_dict = {
    "Personajes": "char",
     "Poderes": "sp",
     "Equipos": "team",
     "Universos": "uni",
     "Creadores": "crea"
     }

df_faltantes = get_faltantes(fal_dict[fal_sel], datos=char)
main_col = list(df_faltantes.columns)[0]

fal_tab.dataframe(df_faltantes.set_index(main_col).isin(["Faltante"]), 
                  use_container_width=True)