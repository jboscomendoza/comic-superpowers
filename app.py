import streamlit as st
import pandas as pd

char = pd.read_parquet("char_data.parquet")

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


sel_char = st.selectbox(
    "Elige un personaje",
    char["char_nombre"].unique()
)

pers = char.loc[char["char_nombre"] == sel_char]

p_1, p_2, p_3 = st.columns(3)

p_1.markdown("### Súperpoderes")
for sp in pers["sp_nombre"].drop_duplicates():
    p_1.markdown(sp)

p_2.markdown("### Equipos")
for team in pers["team_nombre"].drop_duplicates():
    p_2.markdown(team)
    
p_3.markdown("### Universos")
for uni in pers["uni_nombre"].drop_duplicates():
    p_3.markdown(uni)