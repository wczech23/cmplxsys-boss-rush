import math
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from disease_symptoms import disease_symptoms


def build_and_plot_graph(region_code, top_n=50, remove_isolates=True):
    # reading from list of extracted search trends
    df = pd.read_csv("disease_trends_US.csv")
    # selecting the top 50 potential diseases based on search popularity
    df = df.sort_values("PopularityDiff", ascending=False).head(top_n)

    G = nx.Graph()

    # Add nodes (diseases) with attributes
    for _, row in df.iterrows():
        disease = row["Disease"]
        cases = row["PopularityDiff"]
        G.add_node(disease, size=cases)

    # Add edges based on shared symptoms
    disease_list = list(G.nodes())
    for i in range(len(disease_list)):
        for j in range(i + 1, len(disease_list)):
            d1 = disease_list[i]
            d2 = disease_list[j]
            # Get symptom lists from dictionary (empty if not present)
            sym1 = set(disease_symptoms.get(d1, []))
            sym2 = set(disease_symptoms.get(d2, []))
            shared = sym1.intersection(sym2)
            if shared:
                # Edge weight = number of shared symptoms
                G.add_edge(d1, d2, weight=len(shared))

    # Optionally remove isolates (diseases with no edges)
    if remove_isolates:
        isolates = list(nx.isolates(G))
        for iso in isolates:
            G.remove_node(iso)

    # If fewer than 2 nodes remain, skip plotting
    if len(G.nodes()) < 2:
        print(f"[WARNING] Not enough connected diseases to plot a graph")
        return 1
    
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("white")  # White figure bg
    ax.set_facecolor("white")         # White plot bg

    # Choose a layout
    # pos = nx.spring_layout(G, seed=42, k=2.0, iterations=200)  # More spread-out spring
    pos = nx.kamada_kawai_layout(G, weight='weight')  # Often yields less overlap

    popularity_vals = [G.nodes[d]["size"] for d in G.nodes()]
    if not popularity_vals:
        return

    min_val = min(popularity_vals)
    max_val = max(popularity_vals)

    # Log-transform for color
    range_val = max_val - min_val if max_val != min_val else 1
    normalized_vals = [(val - min_val) / range_val for val in popularity_vals]
    vmin = 0
    vmax = 1

    node_colors = normalized_vals
    # Log-transform for size
    # so big differences in case counts don't overshadow everything
    min_size = 200
    max_size = 1000
    node_sizes = [min_size + (max_size - min_size) * norm_val for norm_val in normalized_vals]

    # Edge widths based on shared symptom count
    edge_weights = [G[u][v]["weight"] for u, v in G.edges()]
    # Optional: color edges by weight
    edge_colors = [w for w in edge_weights]
    ew_min, ew_max = min(edge_weights), max(edge_weights)

    edges = nx.draw_networkx_edges(
        G, pos,
        ax=ax,
        width=[0.5 + 1.5*(w - ew_min)/(ew_max - ew_min) if ew_max > ew_min else 1 for w in edge_weights],
        edge_color=edge_colors,  # color by weight
        edge_cmap=cm.Greys,
        edge_vmin=ew_min,
        edge_vmax=ew_max,
        alpha=0.7
    )

    # Draw nodes with color mapped to log10(case counts)
    nodes = nx.draw_networkx_nodes(
        G, pos,
        ax=ax,
        node_size=node_sizes,
        node_color=node_colors,
        cmap=cm.Blues,
        vmin=vmin,
        vmax=vmax,
        alpha=0.9
    )

    # Draw labels (optional bounding box for readability)
    nx.draw_networkx_labels(
        G, pos, ax=ax,
        font_size=8,
        font_color="black",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.7)
    )

    norm_nodes = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sm_nodes = cm.ScalarMappable(cmap=cm.Blues, norm=norm_nodes)
    sm_nodes.set_array([])  # needed for colorbar
    cbar_nodes = fig.colorbar(sm_nodes, ax=ax, fraction=0.046, pad=0.04, location='right')
    cbar_nodes.set_label("Search Popularity (Normalized Score)", fontsize=15)

    # Edge colorbar (shared symptoms)
    norm_edges = mcolors.Normalize(vmin=ew_min, vmax=ew_max)
    sm_edges = cm.ScalarMappable(cmap=cm.Greys, norm=norm_edges)
    sm_edges.set_array([])
    cbar_edges = fig.colorbar(sm_edges, ax=ax, fraction=0.046, pad=0.04, location='left')
    cbar_edges.set_label("Shared Symptoms", fontsize=15)

    ax.set_title(f"Top Diseases Based on Your Symptoms \nand Current Search Trends for {region_code}",fontsize=20)
    ax.set_axis_off()
    fig.tight_layout()

    # Save the figure
    fig.savefig(f"your_disease_graph.png", dpi=150)
    plt.close(fig)