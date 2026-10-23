import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()

rotas = [
    ("GIG", "GRU", 340),
    ("GIG", "BSB", 930),
    ("GRU", "CNF", 490),
    ("GRU", "REC", 2100),
    ("BSB", "CNF", 620),
    ("CNF", "REC", 1650),
]

for origem, destino, distancia in rotas:
    G.add_edge(origem, destino, weight=distancia)

print("Número de aeroportos:", G.number_of_nodes())
print("Número de rotas:", G.number_of_edges())
