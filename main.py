import pandas as pd
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import random

# Load dataset
df = pd.read_csv("data.csv")

# Construct graph-based network
G = nx.Graph()
for _, row in df.iterrows():
    G.add_node(row['Name'], city=row['City'], college=row['College'], branch=row['Branch'], gender=row['Gender'])

# Add edges based on shared college or branch
for _, row in df.iterrows():
    similar_students = df[(df['College'] == row['College']) | (df['Branch'] == row['Branch'])]
    for _, sim_row in similar_students.iterrows():
        if row['Name'] != sim_row['Name']:
            G.add_edge(row['Name'], sim_row['Name'])

# Optimize Node2Vec parameters for faster execution
from node2vec import Node2Vec
node2vec = Node2Vec(G, dimensions=8, walk_length=5, num_walks=50, workers=2)  # Reduced dimensions and walks
model = node2vec.fit(window=3, min_count=1, batch_words=2)  # Optimized parameters

def recommend_friends(user_name, top_n=5):
    if user_name in model.wv:
        recommendations = model.wv.most_similar(user_name, topn=top_n)
        return [rec[0] for rec in recommendations]
    else:
        return random.sample(list(G.nodes), top_n)

# Example usage
print(recommend_friends("Aarav Sharma"))