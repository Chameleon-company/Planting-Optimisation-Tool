# Create a YAML file with pairwise similarity scores between USDA soil texture classes
# using a graph-based adjacency on the USDA texture triangle.
# This is to be added into the config/recommend.yaml file
# Scoring scheme:
#   exact=1.0;
#   1-step=0.8;
#   2-step=0.6;
#   3-step=0.4;
#   >=4-step=0.2
#   Hard incompatibilities = 0.0.

import yaml
from collections import deque

# 12 USDA classes
CLASSES = [
    "sand",
    "loamy sand",
    "sandy loam",
    "loam",
    "silty loam",  # This projects naming convention
    "silt",
    "sandy clay loam",
    "clay loam",
    "silty clay loam",
    "sandy clay",
    "silty clay",
    "clay",
]

# Adjacency graph on the USDA triangle (undirected). Edges represent 1-step neighbors.
# This graph captures polygon border-sharing on the USDA texture triangle.
ADJ = {
    "clay": ["clay loam", "sandy clay", "silty clay"],
    "clay loam": [
        "clay",
        "loam",
        "sandy clay",
        "sandy clay loam",
        "silty loam",
        "silty clay",
        "silty clay loam",
    ],
    "loam": ["clay loam", "sandy clay loam", "sandy loam", "silty loam"],
    "loamy sand": ["sand", "sandy loam"],
    "sand": ["loamy sand"],
    "sandy clay": ["clay", "clay loam", "sandy clay loam"],
    "sandy clay loam": ["clay loam", "loam", "sandy clay", "sandy loam"],
    "sandy loam": ["loam", "loamy sand", "sandy clay loam", "silty loam"],
    "silt": ["silty loam"],
    "silty clay": ["clay", "clay loam", "silty clay loam"],
    "silty clay loam": ["clay loam", "silty loam", "silty clay"],
    "silty loam": ["clay loam", "loam", "sandy loam", "silt", "silty clay loam"],
}

# Hard incompatibilities (pairs forced to 0.0).
HARD_ZERO = [
    ("sand", "clay"),
    ("sand", "silty clay"),
    ("sand", "sandy clay"),
    ("sand", "silt"),
    ("loamy sand", "clay"),
    ("loamy sand", "silty clay"),
    ("loamy sand", "silty clay loam"),
]

# Scoring by shortest-path distance
SCORES_BY_DISTANCE = {
    0: 1.0,  # exact match
    1: 0.8,  # neighbour
    2: 0.6,  # neighbour's neighbour
    3: 0.4,  # neighbour's neighbour's neighbour
}
DEFAULT_FAR_SCORE = 0.2  # for distance >= 4


# Compute all-pairs shortest path distances with Breadth First Search
def shortest_path_distances(adj):
    """
    Compute all-pairs shortest-path distances in an unweighted directed graph
    using Breadth-First Search (BFS).

    This function treats `adj` as an adjacency list mapping each node to its
    iterable of neighbours. For every source node in the global `CLASSES`
    collection, it performs a BFS to compute the minimum number of edges needed
    to reach every other node. Unreachable nodes are assigned `float('inf')`.

    BFS algorithm:
        1. Start from the source node.
        2. Mark it as visited.
        3. Put it in a queue.
        4. While the queue is not empty:
           a. Dequeue a node.
           b. Process it (e.g., print or record).
           c. Enqueue all its unvisited neighbours and mark them visited.

    :param adj: Adjacency list of the graph. Keys are
        nodes, values are iterables of neighbour nodes. The graph is assumed
        to be unweighted and (potentially) directed.

    :returns: A nested dictionary `dists` such that
        `dists[src][dst]` is the shortest-path distance (number of edges)
        from `src` to `dst`. If `dst` is unreachable from `src`, the value is
        `float('inf')`. Distances satisfy `dists[src][src] == 0`.

    Examples:
        >>> from collections import deque
        >>> CLASSES = ['A', 'B', 'C', 'D']  # global in the script
        >>> ADJ = {
        ...     'A': ['B', 'C'],
        ...     'B': ['D'],
        ...     'C': ['D'],
        ...     'D': []
        ... }
        >>> dists = shortest_path_distances(adj)
        >>> dists['A']['D']
        2.0
        >>> dists['B']['C']  # unreachable from B
        inf
    """
    dists = {}
    for src in CLASSES:
        dist = {c: float("inf") for c in CLASSES}
        dist[src] = 0
        q = deque([src])
        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if dist[v] == float("inf"):
                    dist[v] = dist[u] + 1
                    q.append(v)
        dists[src] = dist
    return dists


dists = shortest_path_distances(ADJ)


# Build pairwise score matrix according to rules
def build_pairwise():
    m = {}
    hard_zero_set = set(tuple(sorted(p)) for p in HARD_ZERO)
    for a in CLASSES:
        row = {}
        for b in CLASSES:
            # hard zero overrides
            if tuple(sorted((a, b))) in hard_zero_set:
                score = 0.0
            else:
                d = dists[a][b]
                score = SCORES_BY_DISTANCE.get(d, DEFAULT_FAR_SCORE)
            row[b] = round(score, 3)
            m[a] = row
    return m


pairwise = build_pairwise()

doc = {"features": {"soil_texture": {"compatibility_pairs": pairwise}}}

with open("soil_texture_usda.yaml", "w", encoding="utf-8") as f:
    yaml.safe_dump(doc, f, sort_keys=False)
