import streamlit as st
import pandas as pd
from plotly import graph_objects as go

cols_str = ["char_desc", "sp_nombre", "sp_desc", "team_desc", "gen_nombre"]

char = pd.read_parquet("char_data.parquet")
char[cols_str] = char[cols_str].apply(lambda x: x.str.capitalize())

### ###
### App
### ###
st.markdown("# X-Men")

conteo_sp = (
    char[["char_nombre", "sp_nombre"]]
    .drop_duplicates()
    .groupby("sp_nombre", as_index=False)
    .count()
    .sort_values("char_nombre", ascending=False)
    .reset_index(drop=True)
)
conteo_sp.columns = ["Superpoder", "Conteo"]

st.markdown("## Superpoderes más frecuentes")
st.metric("Superpoderes distintos", len(conteo_sp))
st.bar_chart(conteo_sp, x="Superpoder", y="Conteo")


conteo_team = (
    char[["char_nombre", "team_nombre"]]
    .drop_duplicates()
    .groupby("team_nombre", as_index=False)
    .count()
    .sort_values("char_nombre", ascending=False)
    .reset_index(drop=True)
)
conteo_team.columns = ["Equipo", "Conteo"]
st.markdown("## Equipos más frecuentes")
st.metric("Equipos distintos", len(conteo_team))
st.bar_chart(conteo_team, x="Equipo", y="Conteo")


# Grupos
tab_sp, tab_team, tab_char = st.tabs(["Poderes", "Equipos", "Personajes"])

sel_sp = tab_sp.selectbox("Elige un superpoder", char["sp_nombre"].sort_values().unique())
char_sp = char["char_nombre"].loc[char["sp_nombre"] == sel_sp].drop_duplicates()
tab_sp.metric("Personajes", len(char_sp))
tab_sp.table(char_sp)

sel_team = tab_team.selectbox("Elige un equipo", char["team_nombre"].sort_values().unique())
char_team = char["char_nombre"].loc[char["team_nombre"] == sel_team].drop_duplicates()
tab_team.metric("Personajes", len(char_team))
tab_team.table(char_team)


# Personaje
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

tab_char.metric("Personajes distintos", len(char["char_nombre"].unique()))
tab_char.plotly_chart(gen_bar)

sel_char = tab_char.selectbox(
    "Elige un personaje",
    char["char_nombre"].unique()
)

pers = char.loc[char["char_nombre"] == sel_char]

tab_char.markdown(pers["char_desc"].unique().item())

char_cols = tab_char.columns(3)
contenido = {
    "Súperpoderes": pers["sp_nombre"].drop_duplicates(),
    "Equipos": pers["team_nombre"].drop_duplicates(),
    "Universos": pers["uni_nombre"].drop_duplicates()
}

for i_col, i_key, i_value in zip(char_cols, contenido.keys(), contenido.values()):
    i_col.markdown("### "+i_key)
    for value_in_v in i_value:
        i_col.markdown(value_in_v)