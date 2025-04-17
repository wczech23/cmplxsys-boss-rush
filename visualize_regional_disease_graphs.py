import math
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors

from disease_symptoms import disease_symptoms

def build_and_plot_graph(region_code, top_n=50, remove_isolates=True):
    df = pd.read_csv("disease_cases_by_region.csv")
    df_region = df[df["Region"] == region_code].copy()

    df_region = df_region.sort_values("Cases", ascending=False).head(top_n)

    G = nx.Graph()

    # Add nodes (diseases) with attributes
    for _, row in df_region.iterrows():
        disease = row["Disease"]
        cases = row["Cases"]
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
        print(f"[WARNING] Not enough connected diseases to plot for {region_code}")
        return
    
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor("white")  # White figure bg
    ax.set_facecolor("white")         # White plot bg

    # Choose a layout
    # pos = nx.spring_layout(G, seed=42, k=2.0, iterations=200)  # More spread-out spring
    pos = nx.kamada_kawai_layout(G, weight='weight')  # Often yields less overlap

    # Node size & color in log scale
    # (avoid log(0) by adding 1)
    case_values = [G.nodes[d]["size"] for d in G.nodes()]
    if not case_values:
        return

    min_cases = min(case_values)
    max_cases = max(case_values)

    # Log-transform for color
    node_colors = [math.log10(val + 1) for val in case_values]
    vmin = math.log10(min_cases + 1) if min_cases > 0 else 0
    vmax = math.log10(max_cases + 1)

    # Log-transform for size
    # so big differences in case counts don't overshadow everything
    node_sizes = [200.0 * math.log10(val + 1) for val in case_values]

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
    cbar_nodes = fig.colorbar(sm_nodes, ax=ax, fraction=0.046, pad=0.04)
    cbar_nodes.set_label("Log10(Cases + 1)")

    # Edge colorbar (shared symptoms)
    norm_edges = mcolors.Normalize(vmin=ew_min, vmax=ew_max)
    sm_edges = cm.ScalarMappable(cmap=cm.Greys, norm=norm_edges)
    sm_edges.set_array([])
    cbar_edges = fig.colorbar(sm_edges, ax=ax, fraction=0.046, pad=0.04)
    cbar_edges.set_label("Shared Symptoms")

    ax.set_title(f"Top {top_n} Diseases for {region_code}\n(Node Size & Color = Log Case Count)")
    ax.set_axis_off()
    fig.tight_layout()

    # Save the figure
    fig.savefig(f"{region_code}_disease_graph.png", dpi=150)
    plt.close(fig)
    print(f"[INFO] Saved {region_code}_disease_graph.png")

def build_and_plot_daily_trends():
    return


def main():
    for region in ["USA", "US-MI", "US-CA"]:
        build_and_plot_graph(region_code=region, top_n=50, remove_isolates=True)

if __name__ == "__main__":
    main()
