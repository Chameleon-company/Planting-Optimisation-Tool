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
    "loamy_sand",
    "sandy_loam",
    "loam",
    "silty_loam",  # This projects naming convention
    "silt",
    "sandy_clay_loam",
    "clay_loam",
    "silty_clay_loam",
    "sandy_clay",
    "silty_clay",
    "clay",
]

# Adjacency graph on the USDA triangle (undirected). Edges represent 1-step neighbors.
# This graph captures polygon border-sharing on the USDA texture triangle.
ADJ = {
    "clay": ["clay_loam", "sandy_clay", "silty_clay"],
    "clay_loam": [
        "clay",
        "loam",
        "sandy_clay",
        "sandy_clay_loam",
        "silty_loam",
        "silty_clay",
        "silty_clay_loam",
    ],
    "loam": ["clay_loam", "sandy_clay_loam", "sandy_loam", "silty_loam"],
    "loamy_sand": ["sand", "sandy_loam"],
    "sand": ["loamy_sand"],
    "sandy_clay": ["clay", "clay_loam", "sandy_clay_loam"],
    "sandy_clay_loam": ["clay_loam", "loam", "sandy_clay", "sandy_loam"],
    "sandy_loam": ["loam", "loamy_sand", "sandy_clay_loam", "silty_loam"],
    "silt": ["silty_loam"],
    "silty_clay": ["clay", "clay_loam", "silty_clay_loam"],
    "silty_clay_loam": ["clay_loam", "silty_loam", "silty_clay"],
    "silty_loam": ["clay_loam", "loam", "sandy_loam", "silt", "silty_clay_loam"],
}

# Hard incompatibilities (pairs forced to 0.0).
HARD_ZERO = [
    ("sand", "clay"),
    ("sand", "silty_clay"),
    ("sand", "sandy_clay"),
    ("sand", "silt"),
    ("loamy_sand", "clay"),
    ("loamy_sand", "silty_clay"),
    ("loamy_sand", "silty_clay_loam"),
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
