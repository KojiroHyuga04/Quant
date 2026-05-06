# Quant

Osmaniye Network Optimization Simulation

On this Project; a Linear Programming (LP) based simulation is provided to optimize and analyze the network traffic flow for 6 districts of Osmaniye, Turkey. It calculates the maximum bandwidth capacity between the main backbone (ISP) and the districts while adhering to strict Quality of Service (QoS) constraints.

Project Overview:

The simulation models a network topology consisting of:
Main Source: S_Backbone (ISP)
Intermediate Nodes: Central Stations (Santral)
Sinks (Districts):Bahçe, Düziçi, Hasanbeyli, Kadirli, Sumbas, Toprakkale.

The objective is to maximize the total flow (Mbps) delivered to the districts using the PuLP optimization library, while filtering paths based on:

-Maximum Ping:** 20.0 ms
-Maximum Jitter:** 5.0 ms

Features of Simulation:

- Quality Filtering: Automatically removes edges that do not meet the minimum latency standards.
- Path Enumeration: Finds all valid paths from the backbone to each district within a specific hop cut off.
- LP Optimization: Solves the Max-Flow problem considering link capacities and concurrent usage.
- Visual Analytics: Generates a network flow graph highlighting link types (Fiber, Copper, Radio) and utilization rates.
- Comparison: Includes an improvement analysis using a dataset to see how upgrades affect total throughput.



- `Osmaniye.py`: Main simulation script.
- `Topology.csv`: Initial network data (Nodes, Capacities, Latency).
- `Final_Topology.csv`: Optimized network data for comparison.
- `Result_Table.csv`: Bandwidth results per district.
- `Flow_Graph.png`: Visual representation of the network and flow distribution.
- `Comparison_Chart.png`: Visual comparison between initial and improved states.
