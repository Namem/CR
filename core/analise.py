import numpy as np

def montar_matriz(componentes, frequencia):
    """
    Monta a matriz nodal G e o vetor de fontes I para análise de CA.
    Suporta R, L, C, Z (impedância), e fontes V com fase.
    """
    # Coletar nós
    nos = set()
    for comp in componentes:
        nos.add(comp["n1"])
        nos.add(comp["n2"])
    nos.discard("0")
    nos = sorted(nos)
    mapa_nos = {n: i for i, n in enumerate(nos)}

    N = len(mapa_nos)
    G = np.zeros((N, N), dtype=complex)
    I = np.zeros(N, dtype=complex)
    w = 2 * np.pi * frequencia

    for comp in componentes:
        tipo = comp["tipo"].upper()
        n1 = comp["n1"]
        n2 = comp["n2"]
        val = comp["valor"]

        # Admitância
        if tipo == 'R':
            y = 1 / val
        elif tipo == 'L':
            y = 1 / (1j * w * val)
        elif tipo == 'C':
            y = 1j * w * val
        elif tipo == 'Z':  # suporte real para MOTOR_Y/D
            y = 1 / val
        else:
            y = 0

        if tipo in ['R', 'L', 'C', 'Z']:
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

    print("\n--- MATRIZ G ---")
    print(G)
    print("\n--- VETOR I ---")
    print(I)

    if np.linalg.matrix_rank(G) < len(G):
        raise ValueError("Matriz singular: circuito mal conectado ou sem referência.")

    V = np.linalg.solve(G, I)

    print("\n--- TENSÕES CALCULADAS ---")
    print(V)

    correntes = []
    for comp in componentes:
        tipo = comp["tipo"].upper()
        nome = comp["nome"]
        n1 = comp["n1"]
        n2 = comp["n2"]
        val = comp["valor"]

        if tipo in ['R', 'L', 'C', 'Z']:
            v1 = V[mapa_nos[n1]] if n1 != '0' else 0
            v2 = V[mapa_nos[n2]] if n2 != '0' else 0

            if tipo == 'R':
                Z = val
            elif tipo == 'L':
                Z = 1j * w * val
            elif tipo == 'C':
                Z = 1 / (1j * w * val)
            elif tipo == 'Z':
                Z = val
            else:
                Z = 1

            corrente = (v1 - v2) / Z
            correntes.append({"nome": f"I_{nome}", "valor": corrente})

    return V, mapa_nos, correntes
