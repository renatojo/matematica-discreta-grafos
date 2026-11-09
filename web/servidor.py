"""
Servidor da apresentação — usa SÓ a biblioteca padrão do Python (nada de pip install).

Uso:   python servidor.py        (ou python3 servidor.py)
Pasta: servidor.py + buscador_passagens.html + origens_destinos_unicos.csv + yen.py (seu)
Abre sozinho em http://localhost:8000
"""
import csv, json, os, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

AQUI = os.path.dirname(os.path.abspath(__file__))
PORTA = 8000

# ---------- grafo: grafo[origem][destino] = custo ----------
def carregar_grafo():
    g = {}
    with open(os.path.join(AQUI, "origens_destinos_unicos.csv"), encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            g.setdefault(r["origem"], {})[r["destino"]] = float(r["custo_por_assento"])
            g.setdefault(r["destino"], {})
    return g

GRAFO = carregar_grafo()

# ---------- seu algoritmo ----------
# Crie yen.py com:  def yen(grafo, origem, destino, k): -> [(caminho, custo), ...]
# (caminho = lista de códigos, ex.: ["SBGL", "SBKP", "SBGR"])
try:
    from yen import yen
except ImportError:
    def yen(grafo, origem, destino, k):  # provisório: só o voo direto, para testar a tela
        c = grafo.get(origem, {}).get(destino)
        return [([origem, destino], c)] if c is not None else []

# ---------- HTTP ----------
class Handler(BaseHTTPRequestHandler):
    def _enviar(self, codigo, tipo, corpo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path in ("/", "/index.html"):
            with open(os.path.join(AQUI, "buscador_passagens.html"), "rb") as f:
                return self._enviar(200, "text/html; charset=utf-8", f.read())
        if url.path == "/buscar":
            q = {k: v[0] for k, v in parse_qs(url.query).items()}
            try:
                o, d, k = q["origem"], q["destino"], int(q.get("k", 3))
                res = yen(GRAFO, o, d, k)
                dados = {"caminhos": [{"rota": c, "custo": custo} for c, custo in res]}
                return self._enviar(200, "application/json", json.dumps(dados).encode())
            except Exception as e:
                return self._enviar(400, "application/json", json.dumps({"erro": str(e)}).encode())
        self._enviar(404, "text/plain", b"nao encontrado")

    def log_message(self, *a):  # silencia o log no terminal
        pass

if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORTA), Handler)
    print(f"Rodando em http://localhost:{PORTA}  (Ctrl+C para parar)")
    webbrowser.open(f"http://localhost:{PORTA}")
    srv.serve_forever()