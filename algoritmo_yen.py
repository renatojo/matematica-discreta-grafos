import heapq
# Biblioteca da própria linguagem que permite usar uma lista comum como fila de
# prioridade, ou seja, uma lista da qual sempre se retira o menor elemento.
# Usaremos apenas duas funções:
#   heapq.heappush(heap, item) -> insere um item na fila
#   heapq.heappop(heap)        -> remove e devolve o menor item da fila


def dijkstra(grafo, vertice_origem, vertice_destino,
             arestas_bloqueadas=frozenset(), vertices_bloqueados=frozenset()):
    """Menor caminho do vértice de origem ao vértice de destino.

    Parâmetros:
        grafo: dicionário no formato grafo[u][v] = peso da aresta u -> v.
        arestas_bloqueadas: conjunto de tuplas (u, v) que não podem ser usadas.
        vertices_bloqueados: conjunto de vértices pelos quais não se pode passar.
        (Esses dois bloqueios são usados pelo algoritmo de Yen.)

    Retorna (caminho, custo), ou None se não existir caminho.
    """

    # distancia[v] = menor distância da origem até v encontrada até agora
    distancia = {vertice_origem: 0}

    # anterior[v] = vértice de onde se veio para chegar em v pelo melhor caminho
    anterior = {}

    # fila de prioridade com itens (distância acumulada desde a origem, vértice)
    heap = [(0, vertice_origem)]

    # vértices já processados, cuja distância é definitiva
    visitados = set()

    # enquanto houver vértices pendentes na heap
    while heap:

        # retira o vértice mais próximo da origem (menor distância acumulada)
        distancia_atual, vertice = heapq.heappop(heap)

        # se já foi processado, esta é uma entrada antiga (repetida) da heap:
        # ignora e passa para o próximo elemento
        if vertice in visitados:
            continue

        # marca como visitado: a distância dele agora é definitiva
        visitados.add(vertice)

        # chegamos ao destino: reconstrói o caminho
        if vertice == vertice_destino:
            caminho = [vertice_destino]

            # o dicionário 'anterior' só permite voltar: partindo do destino,
            # acrescenta o vértice de onde se veio, até chegar na origem
            while caminho[-1] != vertice_origem:
                caminho.append(anterior[caminho[-1]])

            # o caminho foi montado do destino para a origem, então inverte a ordem
            caminho.reverse()

            return caminho, distancia_atual

        # para cada vizinho, vê se passar por 'vertice' dá um caminho melhor
        for vizinho, peso in grafo.get(vertice, {}).items():

            # ignora o vizinho se ele estiver bloqueado, ou se a aresta
            # vertice -> vizinho estiver bloqueada (o Yen usa isso para forçar desvios)
            if vizinho in vertices_bloqueados or (vertice, vizinho) in arestas_bloqueadas:
                continue

            # distância até o vizinho passando por 'vertice'
            nova_distancia = distancia_atual + peso

            # se esse caminho é mais curto que o melhor conhecido até o vizinho
            # (infinito, se ainda não conhecemos nenhum), atualiza
            if nova_distancia < distancia.get(vizinho, float("inf")):
                distancia[vizinho] = nova_distancia
                anterior[vizinho] = vertice

                # coloca o vizinho na heap com a nova distância, para ser visitado depois
                heapq.heappush(heap, (nova_distancia, vizinho))

    # a heap esvaziou sem chegar ao destino: não existe caminho
    return None



def custo_do_caminho(grafo, caminho):
    """Calcula o custo total de um caminho (soma dos pesos das arestas)."""
    return sum(grafo[u][v] for u, v in zip(caminho, caminho[1:]))


def yen(grafo, vertice_origem, vertice_destino, k):
    """Retorna uma lista com até k tuplas (caminho, custo), do menor para o maior."""

    # o primeiro menor caminho vem de um Dijkstra normal, sem bloqueios
    primeiro = dijkstra(grafo, vertice_origem, vertice_destino)
    if primeiro is None:
        return []

    encontrados = [primeiro]          # caminhos já confirmados (no máximo k)
    candidatos = []                   # heap de (custo, caminho) ainda não confirmados
    ja_vistos = {tuple(primeiro[0])}  # evita candidatos duplicados (tuple, pois lista não entra em set)

    # enquanto ainda faltam caminhos para chegar a k
    while len(encontrados) < k:

        # pega o último caminho confirmado (só o caminho, sem o custo)
        ultimo = encontrados[-1][0]

        # Tenta desviar em cada vértice do último caminho, menos no destino
        # (por isso len(ultimo) - 1):
        #   ponto_de_desvio --> vértice onde sairemos do caminho antigo
        #   trecho_fixo     --> parte do caminho da origem até o ponto de desvio (inclusive),
        #                       que será mantida igual no novo caminho
        for i in range(len(ultimo) - 1):
            ponto_de_desvio = ultimo[i]
            trecho_fixo = ultimo[: i + 1]

            # Bloqueia a aresta seguinte de todo caminho já encontrado
            # que começa com o mesmo trecho fixo
            arestas_bloqueadas = set()
            for caminho, _ in encontrados:

                # o caminho tem uma aresta depois do trecho fixo (len > i + 1)
                # e começa exatamente com o trecho fixo?
                if len(caminho) > i + 1 and caminho[: i + 1] == trecho_fixo:

                    # bloqueia a aresta que sai do ponto de desvio nesse caminho
                    arestas_bloqueadas.add((caminho[i], caminho[i + 1]))

            # Bloqueia os vértices do trecho fixo (menos o ponto de desvio)
            # para não formar ciclos
            vertices_bloqueados = set(trecho_fixo[:-1])

            # Dijkstra do ponto de desvio até o destino, respeitando os bloqueios
            resultado = dijkstra(
                grafo, ponto_de_desvio, vertice_destino, arestas_bloqueadas, vertices_bloqueados
            )

            # sem caminho possível a partir desse ponto de desvio: tenta o próximo
            if resultado is None:
                continue

            # só interessa o caminho; o custo devolvido cobre apenas o desvio, então é descartado
            desvio, _ = resultado

            # novo candidato = trecho fixo (sem o último vértice, que o desvio já inclui) + desvio
            candidato = trecho_fixo[:-1] + desvio

            # ignora candidatos já vistos antes
            chave = tuple(candidato)
            if chave in ja_vistos:
                continue

            ja_vistos.add(chave)

            # guarda o candidato na heap, com o custo do caminho completo
            heapq.heappush(candidatos, (custo_do_caminho(grafo, candidato), candidato))

        # se depois do for não há nenhum candidato, não existem mais caminhos
        if not candidatos:
            break

        # o candidato de menor custo vira o próximo caminho confirmado
        custo, caminho = heapq.heappop(candidatos)
        encontrados.append((caminho, custo))

    return encontrados
