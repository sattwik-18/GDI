# Document 14 — Object Relationship Graph Engine
## GDI: Spatial and Semantic Object Graph Construction

**Version:** 1.0.0
**Classification:** INTERNAL — ENGINEERING CONFIDENTIAL
**Status:** APPROVED
**Last Updated:** 2026-07-21
**Cross-References:** [05_Genome_Extraction_Engine], [07_Layout_Analysis], [13_Metadata_Analysis], [17_Similarity_Engine]

---

## Table of Contents

1. [Purpose and Forensic Rationale](#1-purpose-and-forensic-rationale)
2. [Feature Groups and Definitions](#2-feature-groups-and-definitions)
3. [Object Extraction and Representation](#3-object-extraction-and-representation)
4. [Graph Construction Topology](#4-graph-construction-topology)
5. [Graph Invariant and Structural Features](#5-graph-invariant-and-structural-features)
6. [Graph Isomorphism and Matching](#6-graph-isomorphism-and-matching)
7. [Spatial Relationship Matrix](#7-spatial-relationship-matrix)
8. [Semantic and Functional Consistency](#8-semantic-and-functional-consistency)
9. [Graph Anomaly Localization](#9-graph-anomaly-localization)
10. [Algorithms and Complexity](#10-algorithms-and-complexity)

---

## 1. Purpose and Forensic Rationale

The Object Relationship Graph (ORG) Engine models a document as a structured graph of interconnected spatial, visual, and semantic objects. While layout analysis measures geometric distributions and typography analyzes glyph properties, the ORG Engine captures the **relational structure and topological hierarchy** of the document.

**Forensic Rationale**:
Documents are constructed according to structural hierarchies (e.g., Header -> Section Title -> Paragraph -> Line -> Character; or Form Label -> Form Input Box -> Signature Line). When a document is manipulated (e.g., swapping a value, adding a fraudulent seal, altering a table row), the geometric layout may look acceptable at first glance, but the topological and relational properties of the graph are broken:
- A text label's nearest neighbor changes
- The containment hierarchy of a bounding box is violated
- Relative directional vectors between key structural elements deviate from the template
- The graph spectral properties (laplacian eigenvalues) shift significantly

By framing document structure as an attributed relational graph (ARG), GDI detects structural forgeries, layout tampering, and object insertion/deletion with mathematical precision.

---

## 2. Feature Groups and Definitions

| Group | Features (std) | Features (deep) | Significance |
|-------|----------------|-----------------|-------------|
| Graph Topology | 25 | 45 | FS1 (Critical) |
| Spatial Relationship Matrix | 15 | 30 | FS1 (Critical) |
| Semantic Consistency | 12 | 25 | FS2 (Major) |
| **Total** | **52** | **100** | — |

---

## 3. Object Extraction and Representation

### 3.1 Graph Node Classification

Every document component is extracted as a node $v_i \in V$ in the graph. Nodes belong to discrete visual/semantic categories:

- `TEXT_BLOCK`: Group of lines forming a logical paragraph
- `TEXT_LINE`: Individual line of text
- `LABEL`: Short text object acting as an identifier or form field descriptor
- `VALUE`: Text object acting as variable user input or form field value
- `IMAGE`: Embedded raster graphic or photograph
- `SIGNATURE`: Dedicated signature image/vector
- `LOGO_SEAL`: Official organization emblem, seal, or watermark
- `TABLE`: Tabular structure containing cells
- `TABLE_CELL`: Individual unit within a table
- `SEPARATOR`: Line, rule, or boundary graphic

### 3.2 Node Attributes

Each node $v_i$ carries a rich set of attributes:
- `bbox`: Absolute bounding box $[x_{min}, y_{min}, x_{max}, y_{max}]$
- `centroid`: Center coordinates $(x_c, y_c)$
- `area`: Bounding box area
- `aspect_ratio`: $width / height$
- `semantic_type`: Node category (from §3.1)
- `content_hash`: Cryptographic/perceptual hash of node content
- `z_index`: Stacking order (for overlapping PDF objects)

---

## 4. Graph Construction Topology

Edges $e_{ij} = (v_i, v_j) \in E$ represent spatial and structural relationships between objects. GDI constructs three distinct graph representations per document page:

### 4.1 Delaunay Triangulation Graph ($G_D$)
Constructed using the centroids of all nodes as vertices. Connects every node to its spatial natural neighbors.
- *Property*: Planar, scale-invariant topology, insensitive to minor isotropic scaling.

### 4.2 K-Nearest Neighbor Graph ($G_k$)
Connects each node to its $k$ spatially nearest neighbors ($k=5$ default).
- *Property*: Captures local clustering and neighborhood density.

### 4.3 Hierarchical Containment & Alignment Tree ($G_H$)
Directed Acyclic Graph (DAG) representing bounding box containment (e.g., Page $\rightarrow$ Table $\rightarrow$ Cell $\rightarrow$ Text) and horizontal/vertical alignment groupings.

### 4.4 Edge Attributes
Every edge $e_{ij}$ carries spatial vector attributes:
- `distance`: Euclidean distance between centroids $d(v_i, v_j)$
- `angle`: Spatial direction angle $\theta(v_i, v_j) = \arctan2(\Delta y, \Delta x)$
- `overlap_ratio`: Intersection over Union (IoU) of bounding boxes
- `relative_scale`: $Area(v_i) / Area(v_j)$

---

## 5. Graph Invariant and Structural Features

Graph invariants are global properties of the graph topology that remain invariant under rigid transformations (rotation, translation) but change under structural manipulation.

### 5.1 Graph Spectral Analysis
Let $A$ be the adjacency matrix of $G_D$ weighted by inverse Euclidean distance $W_{ij} = 1 / d(v_i, v_j)$. The normalized Graph Laplacian is defined as:
$$L = I - D^{-1/2} A D^{-1/2}$$
where $D$ is the degree matrix $D_{ii} = \sum_j A_{ij}$.

**Features Extracted**:
- `objgraph.spectral.eigenvalues`: Top-10 smallest non-zero eigenvalues of $L$ (Laplacian Spectrum)
- `objgraph.spectral.spectral_radius`: Largest eigenvalue of $A$
- `objgraph.spectral.algebraic_connectivity`: Second-smallest eigenvalue of $L$ (Fiedler value)
- `objgraph.spectral.energy`: Sum of absolute eigenvalues of $A$

### 5.2 Topological Metrics

| Feature ID | Description | Formula / Method | Significance |
|------------|-------------|------------------|-------------|
| `objgraph.topo.node_count` | Total graph vertices $|V|$ | Count | FS2 |
| `objgraph.topo.edge_count` | Total graph edges $|E|$ | Count | FS2 |
| `objgraph.topo.density` | Graph edge density | $2|E| / (|V|(|V|-1))$ | FS2 |
| `objgraph.topo.clustering_coeff` | Global clustering coefficient | Transitivity of $G_k$ | FS1 |
| `objgraph.topo.diameter` | Longest shortest path in $G_D$ | Hop count / Distance | FS2 |
| `objgraph.topo.assortativity` | Degree assortativity coefficient | Pearson correlation of degrees | FS2 |
| `objgraph.topo.centrality_std` | Standard deviation of eigenvector centrality | Variation in structural hubs | FS1 |

---

## 6. Graph Isomorphism and Matching

Comparing a submitted document's Object Relationship Graph ($G_S$) against the template's graph ($G_T$) is framed as an **Attributed Graph Matching** problem.

### 6.1 Bipartite Matching via Earth Mover's Distance / Hungarian Algorithm
1. Compute node-to-node cost matrix $C$ between $V_S$ and $V_T$:
   $$C(i, j) = w_1 \cdot d_{spatial}(v_i, v_j) + w_2 \cdot d_{semantic}(v_i, v_j) + w_3 \cdot d_{visual}(v_i, v_j)$$
2. Solve optimal assignment using the Hungarian Algorithm $O(N^3)$ to find node mapping $\pi: V_S \rightarrow V_T$.

### 6.2 Graph Edit Distance (GED)
Measures the minimal sequence of edit operations (node insertion, node deletion, node substitution, edge insertion, edge deletion) required to transform $G_S$ into $G_T$.

$$\text{GED}(G_S, G_T) = \min_{(e_1, \dots, e_k) \in \mathcal{P}(G_S, G_T)} \sum_{i=1}^k c(e_i)$$

- An unmanipulated document yields $\text{GED} \approx 0$ (modulo minor natural variance).
- Inserted fraudulent stamps, text modifications, or removed signatures yield high GED costs.

---

## 7. Spatial Relationship Matrix

The Spatial Relationship Matrix (SRM) encodes pairwise spatial orientation and distance constraints between critical document landmarks (e.g., logo to header, label to signature line).

### 7.1 Matrix Formulation
For a set of $M$ key landmarks, the matrix $R \in \mathbb{R}^{M \times M \times 2}$ records:
- $R_{ij, 0} = d(v_i, v_j) / \text{Page\_Diagonal}$ (Normalized Distance)
- $R_{ij, 1} = \theta(v_i, v_j) / 2\pi$ (Normalized Angle)

### 7.2 Anomaly Score
$$\text{Anomaly}_{SRM} = \frac{1}{M^2} \sum_{i=1}^M \sum_{j=1}^M \left( \left| R^{sub}_{ij,0} - R^{tmpl}_{ij,0} \right| + \left| \text{ang\_diff}(R^{sub}_{ij,1}, R^{tmpl}_{ij,1}) \right| \right)$$

---

## 8. Semantic and Functional Consistency

Documents obey functional pair constraints (e.g., a `LABEL` "Date of Birth:" must have an adjacent `VALUE` node to its right or below it).

### 8.1 Functional Pair Rules
- `LABEL` $\rightarrow$ `VALUE` (spatial proximity & alignment)
- `SIGNATURE_LINE` $\rightarrow$ `SIGNATURE` (containment / vertical stack)
- `LOGO` $\rightarrow$ `HEADER_TEXT` (top page anchor)

### 8.2 Anomaly Metrics
- `objgraph.semantic.orphaned_labels`: Count of labels missing corresponding values
- `objgraph.semantic.unanchored_signatures`: Signatures floating without associated baseline/line
- `objgraph.semantic.type_mismatches`: Nodes whose position matches a template node but whose semantic category differs

---

## 9. Graph Anomaly Localization

When Graph Edit Distance or Spectral divergence flags an anomaly:
1. Identify all nodes $v_i \in V_S$ whose local edit cost $c(v_i)$ exceeds $\mu + 3\sigma$.
2. Compute local subgraph discrepancy around $v_i$.
3. Draw a bounding box around the localized anomalous nodes.
4. Export bounding region to the overall Spatial Anomaly Heatmap.

---

## 10. Algorithms and Complexity

| Process | Algorithm | Time Complexity | Space Complexity |
|---------|-----------|-----------------|------------------|
| Triangulation | Delaunay Triangulation | $O(N \log N)$ | $O(N)$ |
| Spectral Analysis | SciPy Sparse ARPACK (eigsh) | $O(N^2 k)$ | $O(N^2)$ |
| Node Assignment | Hungarian Algorithm (scipy.optimize) | $O(N^3)$ | $O(N^2)$ |
| GED Approximation | Bipartite Graph Edit Distance | $O(N^3)$ | $O(N^2)$ |

*Performance*: For a standard document page with $N=150$ objects, complete graph construction, spectral decomposition, and matching completes in **P50: 1.8s**, **P95: 4.5s**.

---

*Previous: [13_Metadata_Analysis](../13_Metadata_Analysis/README.md)*
*Next: [15_Micro_DNA_Engine](../15_Micro_DNA_Engine/README.md)*
*Return to: [Master Index](../README.md)*
