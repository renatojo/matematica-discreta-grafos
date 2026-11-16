"""Converte dados de ligações entre aeroportos para o grafo usado no algoritmo de Yen.

Formato de entrada (um aeroporto de origem ligado aos demais):
    {
        "SBAR": {0: {"custo_por_assento": 802.11, "empresa": "AZU"},
                 1: {"custo_por_assento": 498.51, "empresa": "GLO"}},
        "SBBE": {0: {"custo_por_assento": 467.10, "empresa": "AZU"}},
        ...
    }

Formato de saída (grafo): grafo[u][v] = peso da aresta u -> v
    {"SBAE": {"SBAR": 498.51, "SBBE": 467.10, ...}, "SBAR": {}, "SBBE": {}, ...}
"""

import ast

def carregar_dados(caminho_arquivo):
    """Lê um arquivo de texto que contém um dicionário Python e devolve esse dicionário."""
    with open(caminho_arquivo, encoding="utf-8") as arquivo:
        # literal_eval só interpreta valores literais (dicionários, números, textos),
        # por isso é mais seguro que eval()
        return ast.literal_eval(arquivo.read())


def _adicionar_aresta(grafo, u, v, peso):
    """Adiciona a aresta u -> v ao grafo, mantendo só a mais barata se ela já existir."""
    # garante que os dois vértices existam como chave do grafo
    grafo.setdefault(u, {})
    grafo.setdefault(v, {})

    if v not in grafo[u] or peso < grafo[u][v]:
        grafo[u][v] = peso


def converter_para_grafo(origem, dados, grafo=None, bidirecional=False):
    """Transforma as ligações de um aeroporto de origem em um grafo.

    Parâmetros:
        origem: código do aeroporto de origem (ex.: "SBAE"). Ele não aparece
            dentro de 'dados', por isso precisa ser informado.
        dados: dicionário {destino: {0: {"custo_por_assento": ..., "empresa": ...}, ...}}.
        grafo: grafo já existente ao qual as arestas serão acrescentadas. Se for None,
            um grafo novo é criado. Serve para juntar vários arquivos (um por origem).
        bidirecional: se True, cria também a aresta de volta (destino -> origem)
            com o mesmo peso.

    Retorna o grafo no formato grafo[u][v] = peso.

    Cada empresa que faz a mesma ligação equivale a uma aresta paralela. Como o
    Dijkstra só aproveita a mais barata, o peso da aresta é o menor
    'custo_por_assento' entre as empresas.
    """
    if grafo is None:
        grafo = {}

    # garante que a origem exista no grafo, mesmo que 'dados' venha vazio
    grafo.setdefault(origem, {})

    for destino, opcoes in dados.items():

        # ligação do aeroporto com ele mesmo não serve para nada: ignora
        if destino == origem:
            continue

        # sem nenhuma empresa para essa ligação: ignora
        if not opcoes:
            continue

        # a empresa mais barata define o peso da aresta
        peso = min(opcao["custo_por_assento"] for opcao in opcoes.values())

        _adicionar_aresta(grafo, origem, destino, peso)
        if bidirecional:
            _adicionar_aresta(grafo, destino, origem, peso)

    return grafo
