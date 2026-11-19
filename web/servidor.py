"""
Servidor da apresentação.
Dependências externas: pandas e networkx (pip install pandas networkx).

Pasta: servidor.py + algoritmo_yen.py + buscador_passagens.html + Embraer_EMAp.png + nomes.json
CSV esperado em ../dados_processados/origem_destino_customedio.csv
Abre sozinho em http://localhost:8000
"""
import json, os, webbrowser
from functools import lru_cache
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import pandas as pd
import networkx as nx
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from algoritmo_de_yen.algoritmo_yen import yen

AQUI = os.path.dirname(os.path.abspath(__file__))
PORTA = 8000
CSV = os.path.join(AQUI, "..", "dados_processados", "origem_destino_customedio.csv")
NOMES_JSON = os.path.join(AQUI, "jsons/nomes.json")
ESTATICOS = {"/Embraer_EMAp.png": "image/png"}
LOCAIS = os.path.join(AQUI, "..", "dados_processados", "locais_aerodromos.csv")
ESTADOS_JSON = os.path.join(AQUI, "jsons/brasil_estados.json")
# ---------- dados: o CSV é lido uma única vez ----------
DF = pd.read_csv(CSV, sep=";", index_col=0)


# ---------- /dados: rotas (do CSV) + nomes (do nomes.json) ----------
def montar_dados():
    rotas = {o: sorted(g["destino"].unique().tolist()) for o, g in DF.groupby("origem")}
    nomes = {}
    if os.path.exists(NOMES_JSON):
        with open(NOMES_JSON, encoding="utf-8") as f:
            nomes = json.load(f)
    else:
        print("AVISO: nomes.json não encontrado; o front mostrará só os códigos ICAO.")
    return json.dumps({"rotas": rotas, "nomes": nomes}, ensure_ascii=False).encode("utf-8")


DADOS_JSON = montar_dados()

def montar_geo():
    aero = pd.read_csv(LOCAIS, sep=";", index_col=0).dropna(subset=["Latitude", "Longitude"])
    aeroportos = {r.ICAO: [float(r.Latitude), float(r.Longitude)] for r in aero.itertuples()}
    estados = []
    if os.path.exists(ESTADOS_JSON):
        with open(ESTADOS_JSON) as f:
            estados = json.load(f)
    else:
        print("AVISO: brasil_estados.json não encontrado; o mapa ficará sem contorno.")
    return json.dumps({"aeroportos": aeroportos, "estados": estados}).encode("utf-8")


GEO_JSON = montar_geo()

# ---------- grafo de um mês ----------
@lru_cache(maxsize=None)
def carregar_grafo(mes):
    df = DF[DF["mes"] == mes]
    return nx.from_pandas_edgelist(
        df,
        source="origem",
        target="destino",
        edge_attr=["custo_por_assento", "empresa"],
        create_using=nx.MultiDiGraph,
    )


@lru_cache(maxsize=None)
def carregar_adjacencia(mes):
    """MultiDiGraph -> {origem: {destino: menor custo}}, o formato que o yen espera."""
    adj = {}
    for u, v, d in carregar_grafo(mes).edges(data=True):
        custo = float(d["custo_por_assento"])
        if v not in adj.setdefault(u, {}) or custo < adj[u][v]:
            adj[u][v] = custo
    return adj


def trechos_da_rota(G, rota):
    trechos = []
    for u, v in zip(rota, rota[1:]):
        melhor = min(G[u][v].values(), key=lambda d: d["custo_por_assento"])
        trechos.append({
            "de": u,
            "para": v,
            "empresa": melhor["empresa"],
            "custo": float(melhor["custo_por_assento"]),
        })
    return trechos


# ---------- HTTP ----------
class Handler(BaseHTTPRequestHandler):
    def _enviar(self, codigo, tipo, corpo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def _arquivo(self, nome, tipo):
        try:
            with open(os.path.join(AQUI, nome), "rb") as f:
                return self._enviar(200, tipo, f.read())
        except FileNotFoundError:
            return self._enviar(404, "text/plain", f"arquivo ausente: {nome}".encode())

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/geo":
            return self._enviar(200, "application/json; charset=utf-8", GEO_JSON)
        if url.path in ("/", "/index.html"):
            return self._arquivo("buscador_passagens.html", "text/html; charset=utf-8")

        if url.path in ESTATICOS:
            return self._arquivo(url.path.lstrip("/"), ESTATICOS[url.path])

        if url.path == "/dados":
            return self._enviar(200, "application/json; charset=utf-8", DADOS_JSON)

        if url.path == "/buscar":
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                origem, destino = q["origem"], q["destino"]
                k, mes = int(q.get("k", 3)), int(q.get("mes", 1))

                G = carregar_grafo(mes)
                resultado = yen(carregar_adjacencia(mes), origem, destino, k)

                dados = {"caminhos": [
                    {"rota": rota, "custo": float(custo), "trechos": trechos_da_rota(G, rota)}
                    for rota, custo in resultado
                ]}
                return self._enviar(200, "application/json", json.dumps(dados).encode())
            except Exception as e:
                return self._enviar(400, "application/json",
                                    json.dumps({"erro": f"{type(e).__name__}: {e}"}).encode())

        self._enviar(404, "text/plain", b"nao encontrado")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    for m in sorted(DF["mes"].unique()):
        carregar_adjacencia(int(m))
    print(f"Meses carregados: {sorted(int(m) for m in DF['mes'].unique())}")

    srv = ThreadingHTTPServer(("127.0.0.1", PORTA), Handler)
    print(f"Rodando em http://localhost:{PORTA}  (Ctrl+C para parar)")
    webbrowser.open(f"http://localhost:{PORTA}")
    srv.serve_forever()