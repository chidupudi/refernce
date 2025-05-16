import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
from joblib import Parallel, delayed

# Sample DataFrame (Replace this with your CSV file reading)
data = pd.read_csv('data.csv', names=['Name', 'City', 'College', 'Age', 'Branch', 'Degree', 'Year', 'Gender', 'Hometown'])

print("Data Loaded Successfully")
print(data.head())

# Build Graph
G = nx.Graph()
similarity_weights = defaultdict(int)

# Add nodes
for _, row in data.iterrows():
    G.add_node(row['Name'], **row.to_dict())

print(f"Added {len(G.nodes())} nodes to the graph")

# Parallel edge creation
def compute_edges(i, student1):
    edges = []
    for j, student2 in data.iterrows():
        if i >= j:
            continue
        common_attributes = sum(
            student1[attr] == student2[attr] for attr in ['City', 'College', 'Branch', 'Degree', 'Year', 'Hometown']
        )
        if common_attributes > 0:
            edges.append((student1['Name'], student2['Name'], common_attributes))
    return edges

# Use parallel processing
results = Parallel(n_jobs=-1)(delayed(compute_edges)(i, student1) for i, student1 in data.iterrows())

# Flatten results and add edges to the graph
for edge_list in results:
    for u, v, weight in edge_list:
        G.add_edge(u, v, weight=weight)
        similarity_weights[(u, v)] = weight

print(f"Added {len(G.edges())} edges to the graph")

# Visualization
pos = nx.spring_layout(G, seed=42)
weights = [G[u][v]['weight'] for u, v in G.edges()]
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color=weights, width=2, cmap=plt.cm.Blues, node_size=500)
nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): G[u][v]['weight'] for u, v in G.edges()})
plt.title('Student Network Graph')
plt.show()

# Friend Recommendation
recommendations = {}

for node in G.nodes():
    neighbors = set(G.neighbors(node))
    potential_friends = set(G.nodes()) - neighbors - {node}

    recommendations[node] = sorted(
        [(friend, sum(G[node][neighbor]['weight'] for neighbor in G.neighbors(node) if G.has_edge(friend, neighbor)))
         for friend in potential_friends],
        key=lambda x: x[1], reverse=True
    )

# Display Recommendations
for student, recs in recommendations.items():
    top_recs = [f"{friend} (Score: {score})" for friend, score in recs[:5] if score > 0]
    print(f"{student}'s Recommended Friends: {', '.join(top_recs) if top_recs else 'No strong matches'}")

print("Recommendation System Execution Completed")
