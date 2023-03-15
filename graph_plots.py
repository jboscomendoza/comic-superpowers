import pandas as pd
from pyvis.network import Network
import networkx as nx


def graph_team(team_to_graph, graph_datos):
    team_cols = graph_datos[["team_nombre", "char_nombre"]].drop_duplicates()
    team_edges = (
        team_cols
        .loc[~team_cols.isin([None]).any(axis=1)]
        .loc[team_cols["team_nombre"] != "X-Men"]
        .rename(columns={"team_nombre":"source", "char_nombre":"target"})
    )
    teams = list(team_cols.sort_values("team_nombre")["team_nombre"].unique())

    in_team = team_edges.loc[team_edges["source"] == team_to_graph]
    out_team = team_edges.loc[team_edges["target"].isin(in_team["target"])]

    graph_team = nx.Graph()
    graph_team = nx.from_pandas_edgelist(out_team)
    nt = Network("435px",
                 width="100%", 
                 font_color="white",
                 bgcolor="#0e1117",
                 notebook=False, 
                 neighborhood_highlight=True)
    nt.from_nx(graph_team)
    for i in nt.nodes:
        i["borderWidth"] = 1
        i["shape"] = "dot"
        if i["id"] == team_to_graph:
            i["group"] = 1
            i["size"] = 25
            i["color"] = "#e3d5ca"
            i["physics"] = False
        elif i["id"] in teams:
            i["group"] = 2
            i["size"] = 20
            i["color"] = "#0077b6"
        else:
            i["group"] = 3
            i["size"] = 15
            i["color"] = "#c36f09"
            i["physics"] = False

    for i in nt.edges:
        i["width"] = 2
    nt.save_graph("teams.html")
    return None


def graph_pairs(ent, tipo, graph_datos):
    """
    ent: _nombre de una entidad sp, team o crea.
    tipo: Uno de sp, team o crea.
    """
    nombre = tipo+"_nombre"
    cols = graph_datos[["char_nombre", nombre]].drop_duplicates()
    in_df = cols.loc[cols[nombre] == ent]
    out_df = cols.loc[cols["char_nombre"].isin(in_df["char_nombre"])].copy()
    out_df.loc[:, "ent"] = ent
    edges = (
        out_df
        .drop("char_nombre", axis=1)
        .value_counts(normalize=True)
        .reset_index()
        .rename(columns={nombre:"source", "ent":"target", 0:"n"})
    )
    
    n_col = edges["n"].copy()
    edges["n"] = ((n_col - n_col.min()) / (n_col.max() - n_col.min()))
    edges["n"] = (edges["n"] * 17.5) + 20
    edges["n"] = edges["n"].fillna(20)
            
    graph = nx.Graph()
    graph = nx.from_pandas_edgelist(edges)
    nt = Network("435px",
                 width="100%", 
                 font_color="white",
                 bgcolor="#0e1117",
                 notebook=False, 
                 neighborhood_highlight=True)
    nt.from_nx(graph)
    
    
    for i in nt.nodes:
        i["borderWidth"] = 1
        i["shape"] = "dot"
        i["size"] = edges["n"].loc[edges["source"] == i["id"]].item()
        if i["id"] == ent:
            i["group"] = 1
            i["color"] = "#0077b6"
            i["physics"] = False
        else:
            i["group"] = 2
            i["color"] = "#c36f09"
        
    for i in nt.edges:
        i["width"] = 2
    nt.save_graph(tipo+".html")
    return None