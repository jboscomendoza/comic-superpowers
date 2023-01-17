import streamlit as st
import pandas as pd
import graph_plots as gp
import matplotlib.pyplot as plt
from plotly import graph_objects as go


st.set_page_config(
    page_title="X-Men Wikidatos",
    page_icon=":book:",
    layout="centered",
    initial_sidebar_state="expanded"
)


def get_conteo(ent_tipo, datos):
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


def get_bars(conteo, rango):
    tick_labs = []
    conteo_r = conteo.loc[conteo["Conteo"].between(rango[0], rango[1])]
    
    x_values = conteo_r.iloc[:, 0]
    y_values = conteo_r.iloc[:, 1]
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
        height=300, 
        margin=dict(t=25, r=0, b=0, l=0),
        xaxis = dict(
            tickmode="array",
            tickvals=x_values,
            ticktext=tick_labs
            )
    )
    return bars
#for i in sp_conteo.iloc[:, 0]:
#    if len(i) > 20:
#        i[0:20] + "..."
#    else:
#        i

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


def crear_descripcion(tipo, s_tab, seleccion):
    mensaje = {
        "char": "Personaje",
        "team": "Personajes que han sido integrantes de este equipo",
        "sp":   "Personajes con este poder",
        "uni":  "Personajes que habitan este universo",
        "crea": "Personajes creados por esta persona",
    } 
    s_tab.markdown(u"## Descripción")
    s_desc = char[tipo+"_desc"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_tab.markdown(s_desc+".")
    s_wiki = char[tipo+"_wiki"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_id = char[tipo+"_id"].loc[char[tipo+"_nombre"] == seleccion].unique().item()
    s_char = char["char_nombre"].loc[char[tipo+"_nombre"] == seleccion].drop_duplicates()
    
    enlace_eswiki   = crear_enlace(s_wiki, "eswiki")
    enlace_wikidata = crear_enlace(s_id, "wikidata")
    s_tab.markdown(f"### Enlaces \n* {enlace_eswiki}  \n* {enlace_wikidata}")
    
    if tipo != "char":
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
char = char.fillna("Faltante")
char = char.replace({"": "Faltante"})
str_cols = ["sp_nombre", "gen_nombre", 
            "sp_desc", "char_desc", "team_desc", "gen_desc", "crea_desc"]
char[str_cols] = char[str_cols].apply(lambda x: x.str.capitalize())


# Elementos resumen
sp_conteo, team_conteo, crea_conteo, gen_conteo = [get_conteo(i, char) for i in [
    "sp", "team", "crea", "gen"]]

totales = {
    "Personajes": len(char["char_nombre"].unique()),
    "Poderes": len(sp_conteo),
    "Equipos": len (team_conteo),
    "Creadores": len (crea_conteo)
}


### ###
### App
### ###
st.markdown("# X-Men - Wikidatos")


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
char_tab.markdown("## Elige un personaje")
char_sel = char_tab.selectbox(
    " personaje",
    options=char["char_nombre"].unique(),
    label_visibility="collapsed"
)

pers = char.loc[char["char_nombre"] == char_sel]

char_desc = pers["char_desc"].unique().item()

char_wiki = pers["char_wiki"].unique().item()
char_wiki = pers["char_id"].unique().item()

crear_descripcion("char", char_tab, char_sel)

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
sp_tab.markdown("## Elige un poder")
sp_sel = sp_tab.selectbox(
    "Elige un poder", 
    options=char["sp_nombre"].sort_values().unique(),
    label_visibility="collapsed")

crear_descripcion("sp", sp_tab, sp_sel)

sp_tab.markdown(u"## Relación entre poderes")
sp_fig = gp.graph_pairs(sp_sel, "sp", char)
sp_tab.pyplot(sp_fig, facecolor="#0e1117")


## Equipos
team_tab.markdown("## Elige un equipo")
team_sel = team_tab.selectbox(
    "Elige un equipo", 
    options=char["team_nombre"].sort_values().unique(),
    label_visibility="collapsed"
    )

crear_descripcion("team", team_tab, team_sel)

team_fig, team_ax = plt.subplots()
team_ax.set_frame_on(False)
gp.graph_team(team_sel, char)
team_tab.markdown(u"## Relación entre equipos")
team_tab.pyplot(team_fig, facecolor="#0e1117")


## Creadores
crea_tab.markdown("## Elige un creador")
crea_sel = crea_tab.selectbox(
    "Elige un creador", 
    options=char["crea_nombre"].sort_values().unique(),
    label_visibility="collapsed"
    )

crear_descripcion("crea", crea_tab, crea_sel)

crea_tab.markdown(u"## Colaboración entre creadores")
crea_fig = gp.graph_pairs(crea_sel, "crea", char)
crea_tab.pyplot(crea_fig, facecolor="#0e1117")


## Resumen
bar_tab.markdown(u"## Totales")
metric_cols = bar_tab.columns(len(totales))
for cont_k, cont_v, cont_col in zip(totales.keys(), totales.values(), metric_cols):
    cont_col.metric(cont_k, cont_v)

bar_tab.markdown(u"### Rango de frecuencia")
rango_frecuencia = bar_tab.slider(
    "Rango de frecuencia",
    label_visibility="collapsed",
    min_value=1, 
    max_value=100, 
    value=(1, 100)
    )
sp_bar, team_bar, crea_bar, gen_bar = [get_bars(i, rango_frecuencia) for i in [
    sp_conteo, team_conteo, crea_conteo, gen_conteo]]

bar_tab.markdown(u"## Personajes por género")
bar_tab.plotly_chart(gen_bar)

bar_tab.markdown("## Poderes más frecuentes")
bar_tab.plotly_chart(sp_bar)

bar_tab.markdown(u"## Equipos con más integrantes")
bar_tab.plotly_chart(team_bar)

bar_tab.markdown(u"## Personajes por creador")
bar_tab.plotly_chart(crea_bar)


## Faltantes
fal_tab.markdown("## Entradas con datos faltantes")

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

fal_tab.dataframe(
    get_faltantes(fal_dict[fal_sel], datos=char),
    use_container_width=True
    )