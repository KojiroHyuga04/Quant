# Quant

Osmaniye Network Optimization Simulation

Real-World Problem Context:

With the rapid digitalization of public services and increasing residential demand, the province of Osmaniye requires a robust telecommunications backbone. The six districts—Bahçe, Düziçi, Hasanbeyli, Kadirli, Sumbas, and Toprakkale—rely on a mix of fiber, copper, and radio links. Ensuring fair and high-speed internet access across these varying geographies is a critical infrastructure challenge for regional development and disaster resilience.

Problem Definition:

The primary objective is to calculate the Maximum Flow of data (bandwidth in Mbps) that can be delivered from the main backbone (ISP) to each of the six districts simultaneously. The problem is constrained by:
Capacity Constraints: Each physical link has a fixed upper limit.
Quality of Service (QoS) Constraints: Paths must maintain a total Ping ≤ 20.0 ms and Jitter ≤ 5.0 ms to be considered "valid."
Topological Constraints: Data must flow through intermediate central stations before reaching the districts.

Network Model:
The network is modeled as a **Directed Graph (DiGraph)** $G = (V, E)$. 
$V$ (Nodes): Represents the ISP source, 6 Central Stations and 6 District sinks.
$E$ (Edges): Represents physical connections which they've characterized by bandwidth capacity, latency (ping) and stability (jitter).


Nodes and Edges:

The current topology consists of 13 primary nodes and 15 edges:
Source Node: S_Backbone (ISP)
Intermediate Nodes (Centrals): 'Santral_Bahce', 'Santral_Duzici' etc.
Sink Nodes (Districts):`Bahce`, `Duzici`, `Hasanbeyli`, `Kadirli`, `Sumbas`, `Toprakkale`.
Link Types: Fiber (High capacity), Copper (Medium capacity) and Radio Links (Low capacity/High latency).

Selected Algorithm:

The solution utilizes a Path-Flow Linear Programming (LP) formulation:
Path Enumeration: All simple paths from source to each sink are identified using a Depth-First Search (DFS) algorithm with a hop-cutoff.
Filtering: Paths exceeding QoS limits (Ping/Jitter) are eliminated.
Optimization: A Linear Programming model maximizes the sum of flows through valid paths subject to the sum of flows on any edge not exceeding its capacity.

Python Implementation:

The project is implemented using the following libraries:
PuLP: To model and solve the Linear Programming problem.
NetworkX: For graph construction and pathfinding.
Pandas: For managing link data and generating results.
Matplotlib: For visualizing the flow distribution and link utilization.


Results:

The simulation identified that the current infrastructure supports a total flow of approximately 3,650 Mbps.
Kadirli & Düziçi: Received full requested capacity due to fiber connectivity.
Hasanbeyli & Sumbas: Received 0 Mbps in the initial model because their radio-link latencies exceeded the 20ms quality threshold.
Improvement Scenario: Upgrading Hasanbeyli and Sumbas to fiber increased the total provincial flow to 5,550 Mbps, which it's representing a significant gain in network equity.

Managerial Interpretation:

From a managerial perspective, the results indicate a clear digital divide. While the backbone is sufficient, the "last-mile" radio connections to Hasanbeyli and Sumbas are critical bottlenecks. Investors and policymakers should prioritize upgrading these specific radio links to fiber, as they currently fail to meet modern QoS standards.

How to Run the Code:
    
Library Installation:

   bash
   pip install pandas pulp networkx matplotlib
    
Data Preparation: Ensuring `Topology.csv` is in the root directory.

Code Execution:

    bash
    python maxflow.py
   

References:

Mitchell, S. (2020). *PuLP: A Linear Programming Modeler for Python*.
Hagberg, A., & Conway, D. (2020). *NetworkX: Network Analysis in Python*.
Ahuja, R. K., Magnanti, T. L., & Orlin, J. B. (1993). *Network Flows: Theory, Algorithms, and Applications*.



- `Osmaniye.py`: Main simulation script.
- `Topology.csv`: Initial network data (Nodes, Capacities, Latency).
- `Final_Topology.csv`: Optimized network data for comparison.
- `Result_Table.csv`: Bandwidth results per district.
- `Flow_Graph.png`: Visual representation of the network and flow distribution.
- `Comparison_Chart.png`: Visual comparison between initial and improved states.
