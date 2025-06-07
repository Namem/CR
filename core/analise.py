# core/analise.py

import numpy as np

def montar_matriz(componentes, frequencia):
    """
    Monta o sistema de equações nodais para análise CA usando impedâncias complexas.
    Retorna:
    - V: tensões nos nós
    - mapa_nos: mapeamento de nome → índice
    - correntes: lista de dicionários com correntes por componente
    """
    # Mapear nós e criar índices
    nos = set()
    for comp in componentes:
        nos.add(comp["n1"])
        nos.add(comp["n2"])
    nos.discard("0")  # nó terra
    nos = sorted(nos)
    mapa_nos = {n: i for i, n in enumerate(nos)}

    N = len(mapa_nos)
    G = np.zeros((N, N), dtype=complex)
    I = np.zeros(N, dtype=complex)
    w = 2 * np.pi * frequencia

    for comp in componentes:
        n1 = comp["n1"]
        n2 = comp["n2"]
        tipo = comp["tipo"].upper()
        val = comp["valor"]

        y = 0
        if tipo == 'R':
            y = 1 / val
        elif tipo == 'L':
            y = 1 / (1j * w * val)
        elif tipo == 'C':
            y = 1j * w * val

        if tipo in ['R', 'L', 'C']:
            if n1 != '0':
                i = mapa_nos[n1]
                G[i, i] += y
            if n2 != '0':
                j = mapa_nos[n2]
                G[j, j] += y
            if n1 != '0' and n2 != '0':
                i = mapa_nos[n1]
                j = mapa_nos[n2]
                G[i, j] -= y
                G[j, i] -= y

        if tipo == 'V':
            fase = comp.get("fase", 0.0)
            fonte = val * np.exp(1j * np.deg2rad(fase))
            if n1 != '0':
                I[mapa_nos[n1]] += fonte
            if n2 != '0':
                I[mapa_nos[n2]] -= fonte

    # Resolver G.V = I
    V = np.linalg.solve(G, I)

    # DEBUG opcional
    print("\n--- MATRIZ G ---")
    print(G)
    print("\n--- VETOR I ---")
    print(I)
    print("\n--- TENSÕES CALCULADAS (V) ---")
    print(V)

    # Calcular correntes por componente
    correntes = []
    for comp in componentes:
        tipo = comp["tipo"].upper()
        nome = comp["nome"]
        n1 = comp["n1"]
        n2 = comp["n2"]
        val = comp["valor"]

        if tipo in ['R', 'L', 'C']:
            v1 = V[mapa_nos[n1]] if n1 != '0' else 0
            v2 = V[mapa_nos[n2]] if n2 != '0' else 0
            Z = None

            if tipo == 'R':
                Z = val
            elif tipo == 'L':
                Z = 1j * w * val
            elif tipo == 'C':
                Z = 1 / (1j * w * val)

            Icomp = (v1 - v2) / Z
            correntes.append({"nome": f"I_{nome}", "valor": Icomp})

    return V, mapa_nos, correntes
