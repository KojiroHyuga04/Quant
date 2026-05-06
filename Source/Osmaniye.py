import pandas as pd
import pulp
import networkx as nx
import matplotlib.pyplot as plt


CSV_PATH = "Topology.csv"
SOURCE = "S_Backbone"
SINKS = ["Bahce", "Duzici", "Hasanbeyli", "Kadirli", "Sumbas", "Toprakkale"]

MAX_PING = 20.0     # ms
MAX_JITTER = 5.0    # ms
PATH_CUTOFF = 6     # max number of edges in a path


# We're loading the data on this step and filtering the edges.

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    before = len(df)
    df = df[(df["ping_ms"] <= MAX_PING) &
            (df["jitter_ms"] <= MAX_JITTER)].copy()
    after = len(df)
    if before != after:
        print(f"[Filter] {before - after} edges removed due to quality "
              f"constraints ({after} edges remain).")
    return df



# Valid paths are enumerated on this step.

def enumerate_valid_paths(df, source, sinks):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row["source"], row["target"],
                   ping=row["ping_ms"], jitter=row["jitter_ms"])

    valid = {s: [] for s in sinks}
    for sink in sinks:
        if not G.has_node(sink):
            continue
        for path in nx.all_simple_paths(G, source, sink, cutoff=PATH_CUTOFF):
            ping_total = sum(G[path[i]][path[i+1]]["ping"]
                             for i in range(len(path) - 1))
            jitter_total = sum(G[path[i]][path[i+1]]["jitter"]
                               for i in range(len(path) - 1))
            if ping_total <= MAX_PING and jitter_total <= MAX_JITTER:
                valid[sink].append({
                    "path": path,
                    "edges": [(path[i], path[i+1]) for i in range(len(path)-1)],
                    "ping": round(ping_total, 2),
                    "jitter": round(jitter_total, 2),
                })
    return valid



# Path-flow LP model

def solve_max_flow(df, valid_paths):
    """
    Decision variables: f_p (flow amount per path, in Mbps)
    Objective: max Sum(f_p)
    Constraint: for each edge, the total flow of paths using it
                must not exceed the edge capacity.
    """
    all_paths = []
    for sink, plist in valid_paths.items():
        for p in plist:
            all_paths.append({
                "sink": sink,
                "path": p["path"],
                "edges": p["edges"],
                "ping": p["ping"],
                "jitter": p["jitter"],
            })

    if not all_paths:
        return "Infeasible", 0.0, []

    model = pulp.LpProblem("Osmaniye_MaxFlow", pulp.LpMaximize)
    f = {idx: pulp.LpVariable(f"f_{idx}", lowBound=0)
         for idx in range(len(all_paths))}

    model += pulp.lpSum(f[idx] for idx in range(len(all_paths))), "Total_Flow"

    edge_capacity = {(r["source"], r["target"]): r["capacity_mbps"]
                     for _, r in df.iterrows()}
    for (u, v), cap in edge_capacity.items():
        using_paths = [idx for idx, p in enumerate(all_paths)
                       if (u, v) in p["edges"]]
        if using_paths:
            model += (pulp.lpSum(f[idx] for idx in using_paths) <= cap,
                      f"Cap_{u}_{v}")

    model.solve(pulp.PULP_CBC_CMD(msg=0))
    status = pulp.LpStatus[model.status]
    total_flow = pulp.value(model.objective) or 0.0

    for idx, p in enumerate(all_paths):
        p["flow"] = round(pulp.value(f[idx]) or 0.0, 2)

    return status, total_flow, all_paths



# Result Table for Bandwidth per Districts:

def build_result_table(all_paths, sinks):
    rows = []
    for sink in sinks:
        used = [p for p in all_paths if p["sink"] == sink and p["flow"] > 1e-6]
        if not used:
            rows.append({
                "district": sink,
                "delivered_flow_mbps": 0.0,
                "used_path": "(none - not reachable)",
                "path_ping_ms": None,
                "path_jitter_ms": None,
            })
        else:
            for p in used:
                rows.append({
                    "district": sink,
                    "delivered_flow_mbps": p["flow"],
                    "used_path": " -> ".join(p["path"]),
                    "path_ping_ms": p["ping"],
                    "path_jitter_ms": p["jitter"],
                })
    return pd.DataFrame(rows)



# Edge utilization analysis is actualized.

def edge_utilization(df, all_paths):
    edge_flow = {}
    for p in all_paths:
        for e in p["edges"]:
            edge_flow[e] = edge_flow.get(e, 0) + p["flow"]

    rows = []
    for _, r in df.iterrows():
        e = (r["source"], r["target"])
        flow = edge_flow.get(e, 0)
        cap = r["capacity_mbps"]
        rows.append({
            "edge": f"{r['source']} -> {r['target']}",
            "flow_mbps": round(flow, 1),
            "capacity_mbps": cap,
            "utilization_%": round(flow / cap * 100, 1) if cap > 0 else 0,
            "link_type": r["link_type"],
        })
    return pd.DataFrame(rows).sort_values("utilization_%", ascending=False)



# Flow graph is virtualized.

def plot_flow_graph(df, all_paths, save_path):
    G = nx.DiGraph()
    edge_flow = {}
    for p in all_paths:
        for e in p["edges"]:
            edge_flow[e] = edge_flow.get(e, 0) + p["flow"]

    for _, row in df.iterrows():
        e = (row["source"], row["target"])
        G.add_edge(e[0], e[1],
                   capacity=row["capacity_mbps"],
                   flow=edge_flow.get(e, 0),
                   link_type=row["link_type"])

    pos = {"S_Backbone": (0, 3)}
    centrals = ["Santral_Bahce", "Santral_Duzici", "Santral_Hasanbeyli",
                "Santral_Kadirli", "Santral_Sumbas", "Santral_Toprakkale"]
    districts = ["Bahce", "Duzici", "Hasanbeyli", "Kadirli", "Sumbas", "Toprakkale"]
    for i, s in enumerate(centrals):
        pos[s] = (i * 2 - 5, 1.5)
    for i, c in enumerate(districts):
        pos[c] = (i * 2 - 5, 0)

    fig, ax = plt.subplots(figsize=(15, 8))

    node_colors = []
    for n in G.nodes():
        if n == "S_Backbone":
            node_colors.append("#1f77b4")
        elif n.startswith("Santral_"):
            node_colors.append("#ff7f0e")
        else:
            node_colors.append("#2ca02c")
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color=node_colors,
                           edgecolors="black", linewidths=1.5, ax=ax)

    color_map = {"fiber": "#0066cc", "bakir": "#cc6600", "radyo": "#990099"}
    for u, v, d in G.edges(data=True):
        flow = d["flow"]
        cap = d["capacity"]
        ratio = flow / cap if cap > 0 else 0
        width = 0.7 + ratio * 6
        alpha = 1.0 if flow > 0 else 0.2
        color = color_map.get(d["link_type"], "gray")
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=width,
                               edge_color=color, alpha=alpha, ax=ax,
                               arrows=True, arrowsize=15,
                               connectionstyle="arc3,rad=0.05")

    labels = {n: n.replace("Santral_", "S_").replace("S_Backbone", "ISP")
              for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=8,
                            font_weight="bold", ax=ax)

    edge_labels = {(u, v): f"{d['flow']:.0f}/{d['capacity']:.0f}"
                   for u, v, d in G.edges(data=True) if d["flow"] > 1e-6}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=7, ax=ax,
                                 bbox=dict(facecolor="white",
                                           edgecolor="none", alpha=0.7))

    from matplotlib.lines import Line2D
    legend = [
        Line2D([0], [0], color="#0066cc", lw=3, label="Fiber"),
        Line2D([0], [0], color="#cc6600", lw=3, label="Copper"),
        Line2D([0], [0], color="#990099", lw=3, label="Radio"),
    ]
    ax.legend(handles=legend, loc="upper right", fontsize=9)
    ax.set_title("Osmaniye 6 Districts - Maximum Flow Result\n"
                 "(Edge labels: used/capacity Mbps)",
                 fontsize=12, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=120, bbox_inches="tight")
    plt.close()



# Main execution

if __name__ == "__main__":
    print("=" * 70)
    print("  OSMANIYE 6 DISTRICTS - MAXIMUM FLOW SIMULATION")
    print("=" * 70)

    df = load_data(CSV_PATH)
    print(f"\n[1/5] Dataset loaded: {len(df)} edges, "
          f"{len(set(df['source']) | set(df['target']))} nodes")

    valid = enumerate_valid_paths(df, SOURCE, SINKS)
    print(f"\n[2/5] Valid paths (ping<={MAX_PING}, jitter<={MAX_JITTER}):")
    for sink, plist in valid.items():
        flag = "OK" if plist else "X "
        print(f"      [{flag}] {sink:12s}: {len(plist)} path(s)")

    status, total_flow, all_paths = solve_max_flow(df, valid)
    print(f"\n[3/5] LP solver: {status}")
    print(f"      Total max flow: {total_flow:.1f} Mbps")

    result = build_result_table(all_paths, SINKS)
    print(f"\n[4/5] RESULT TABLE:")
    print("=" * 70)
    print(result.to_string(index=False))

    summary = (result.groupby("district")["delivered_flow_mbps"].sum()
               .reset_index().sort_values("delivered_flow_mbps", ascending=False))
    summary["vs_average"] = summary["delivered_flow_mbps"].apply(
        lambda x: "above" if x > summary["delivered_flow_mbps"].mean() else "below")
    print(f"\n      Per-district totals (mean: "
          f"{summary['delivered_flow_mbps'].mean():.1f} Mbps):")
    print(summary.to_string(index=False))

    eu = edge_utilization(df, all_paths)
    print(f"\n[5/5] Edge utilization (top 5):")
    print(eu.head(5).to_string(index=False))

    result.to_csv("result_table.csv", index=False)
    plot_flow_graph(df, all_paths, "flow_graph.png")
    print(f"\n[Output] result_table.csv and flow_graph.png saved.")
