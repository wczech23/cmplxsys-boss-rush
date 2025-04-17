import networkx as nx
from disease_symptoms import disease_symptoms
import matplotlib.pyplot as plt

# Create graph
G = nx.Graph()

# Add nodes
for disease in disease_symptoms:
    G.add_node(disease)

# Add edges based on symptom similarity
def compute_similarity(symptoms1, symptoms2):
    shared = set(symptoms1) & set(symptoms2)
    return len(shared)

for d1 in disease_symptoms:
    for d2 in disease_symptoms:
        if d1 != d2:
            sim = compute_similarity(disease_symptoms[d1], disease_symptoms[d2])
            if sim > 0:
                G.add_edge(d1, d2, weight=sim)

# Draw graph
pos = nx.spring_layout(G, seed=42)
weights = [G[u][v]['weight'] for u, v in G.edges()]
nx.draw(G, pos, with_labels=True, width=weights, node_color='lightblue', font_weight='bold')
plt.title("Disease Similarity Based on Shared Symptoms")
plt.show()