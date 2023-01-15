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
    plot_graph_team = nx.draw_networkx(graph_team,
                    with_labels=True,
                    alpha=.85,
                    node_size=150,
                    node_color="#a2d2ff",
                    edge_color="#ffb703",
                    font_size=8)
    return plot_graph_team


def graph_sp(sp_to_graph, graph_datos):
    sp_cols = graph_datos[["char_nombre", "sp_nombre"]].drop_duplicates()
    in_sp = sp_cols.loc[sp_cols["sp_nombre"] == sp_to_graph]
    out_sp = sp_cols.loc[sp_cols["char_nombre"].isin(in_sp["char_nombre"])]
    out_sp["my_sp"] = sp_to_graph
    sp_edges = (
        out_sp
        .drop("char_nombre", axis=1)
        .value_counts()
        .reset_index()
        .rename(columns={"sp_nombre":"source", "my_sp":"target", 0:"n"})
    )
    graph_sp = nx.Graph()
    graph_sp = nx.from_pandas_edgelist(sp_edges)
    plot_graph_sp = nx.draw_networkx(graph_sp, 
                    node_size = sp_edges["n"]*150,
                    alpha=.85,
                    node_color="#a2d2ff",
                    edge_color="#ffb703",
                    font_size=10)
    return plot_graph_sp