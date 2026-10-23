
import folium
import networkx as nx
import webbrowser
import os

# Coordenadas dos aeroportos: latitude, longitude
aeroportos = {
    "GIG": {"nome": "Rio de Janeiro", "coord": [-22.81, -43.25]},
    "GRU": {"nome": "São Paulo", "coord": [-23.43, -46.47]},
    "BSB": {"nome": "Brasília", "coord": [-15.87, -47.92]},
    "CNF": {"nome": "Belo Horizonte", "coord": [-19.63, -43.97]},
    "REC": {"nome": "Recife", "coord": [-8.13, -34.92]}
}

# Grafo dirigido: rotas e distâncias aproximadas em km
G = nx.DiGraph()

rotas = [
    ("GIG", "GRU", 340),
    ("GIG", "BSB", 930),
    ("GRU", "CNF", 490),
    ("GRU", "REC", 2100),
    ("BSB", "CNF", 620),
    ("CNF", "REC", 1650)
]

for origem, destino, distancia in rotas:
    G.add_edge(origem, destino, weight=distancia)

# Simula o bloqueio da rota São Paulo -> Recife
rotas_bloqueadas = [("GRU", "REC")]

# Cria uma cópia do grafo após a tempestade
G_tempestade = G.copy()
G_tempestade.remove_edges_from(rotas_bloqueadas)

# Centraliza o mapa aproximadamente no Brasil
mapa = folium.Map(
    location=[-15.0, -43.0],
    zoom_start=4,
    tiles="OpenStreetMap"
)

# Adiciona marcadores para os aeroportos
for codigo, dados in aeroportos.items():
    folium.Marker(
        location=dados["coord"],
        tooltip=codigo,
        popup=f"{codigo} — {dados['nome']}",
        icon=folium.Icon(color="blue", icon="plane", prefix="fa")
    ).add_to(mapa)

# Desenha as rotas disponíveis em verde
for origem, destino, dados in G_tempestade.edges(data=True):
    ponto_origem = aeroportos[origem]["coord"]
    ponto_destino = aeroportos[destino]["coord"]

    folium.PolyLine(
        locations=[ponto_origem, ponto_destino],
        color="green",
        weight=3,
        opacity=0.8,
        tooltip=(
            f"{origem} → {destino}: "
            f"{dados['weight']} km (aprox.)"
        )
    ).add_to(mapa)

# Desenha as rotas bloqueadas em vermelho tracejado
for origem, destino in rotas_bloqueadas:
    ponto_origem = aeroportos[origem]["coord"]
    ponto_destino = aeroportos[destino]["coord"]

    folium.PolyLine(
        locations=[ponto_origem, ponto_destino],
        color="red",
        weight=4,
        opacity=0.9,
        dash_array="8, 8",
        tooltip=f"BLOQUEADA: {origem} → {destino}"
    ).add_to(mapa)

# Calcula o menor caminho antes e depois da tempestade
origem = "GIG"
destino = "REC"

for nome, grafo in [
    ("Antes da tempestade", G),
    ("Depois da tempestade", G_tempestade)
]:
    try:
        caminho = nx.dijkstra_path(
            grafo, origem, destino, weight="weight"
        )
        distancia = nx.dijkstra_path_length(
            grafo, origem, destino, weight="weight"
        )
        print(f"\n{nome}:")
        print("Caminho:", " -> ".join(caminho))
        print(f"Distância total: {distancia} km")
    except nx.NetworkXNoPath:
        print(f"\n{nome}: não existe caminho entre {origem} e {destino}.")

# Legenda
legenda = """
<div style="
position: fixed; bottom: 30px; left: 30px; width: 220px;
background-color: white; border: 2px solid grey; z-index: 9999;
padding: 10px; font-size: 14px;">
<b>Legenda</b><br>
<span style="color:green;">━━</span> Rota disponível<br>
<span style="color:red;">┄┄</span> Rota bloqueada pela tempestade<br>
🔵 Aeroporto
</div>
"""
mapa.get_root().html.add_child(folium.Element(legenda))

# Salva e abre o mapa no navegador
arquivo = os.path.abspath("mapa_aereo.html")
mapa.save(arquivo)

print(f"\nMapa salvo em: {arquivo}")
webbrowser.open("file://" + arquivo)

