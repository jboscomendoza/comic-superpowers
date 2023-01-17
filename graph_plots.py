import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def graph_team(team_to_graph, graph_datos):
    team_cols = graph_datos[["team_nombre", "char_nombre"]].drop_duplicates()
    team_edges = (
        team_cols
        .loc[~team_cols.isin([None]).any(axis=1)]
        .loc[team_cols["team_nombre"] != "X-Men"]
        .rename(columns={"team_nombre":"source", "char_nombre":"target"})
    )
    team_edges
    in_team = team_edges.loc[team_edges["source"] == team_to_graph]
    out_team = team_edges.loc[team_edges["target"].isin(in_team["target"])]

    graph_team = nx.Graph()
    graph_team = nx.from_pandas_edgelist(out_team)
    team_graph_sp = nx.draw_networkx(graph_team,
                    with_labels=True,
                    node_size=200,
                    font_color="#ffffff",
                    node_color="#023e7d",
                    edge_color="#c36f09",
                    font_size=9)
    return team_graph_sp


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
        .value_counts()
        .reset_index()
        .rename(columns={nombre:"source", "ent":"target", 0:"n"})
    )
    fig, ax = plt.subplots()
    ax.set_frame_on(False)
    graph = nx.Graph()
    graph = nx.from_pandas_edgelist(edges)
    nx.draw_networkx(graph, 
                    node_size = edges["n"]*200,
                    font_color="#ffffff",
                    node_color="#023e7d",
                    edge_color="#c36f09",
                    font_size=9)
    return fig