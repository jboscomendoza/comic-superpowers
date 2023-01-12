import streamlit as st
import pandas as pd

cols_str = ["char_desc", "sp_nombre", "sp_desc", "team_desc"]

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
sel_char = tab_char.selectbox(
    "Elige un personaje",
    char["char_nombre"].unique()
)

pers = char.loc[char["char_nombre"] == sel_char]

p_1, p_2, p_3 = tab_char.columns(3)

p_1.markdown("### Súperpoderes")
for sp in pers["sp_nombre"].drop_duplicates():
    p_1.markdown(sp)

p_2.markdown("### Equipos")
for team in pers["team_nombre"].drop_duplicates():
    p_2.markdown(team)
    
p_3.markdown("### Universos")
for uni in pers["uni_nombre"].drop_duplicates():
    p_3.markdown(uni)