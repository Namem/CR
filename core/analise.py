# core/analise.py

import numpy as np

def montar_matriz(componentes, frequencia):
    """
    Monta a matriz nodal G e o vetor de fontes I para análise de CA.
    Suporta R, L, C, Z (impedância), e fontes V com fase.
    Calcula tensões nodais, correntes de ramo e potências nos componentes.
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

    # Define uma condutância muito alta para modelar fontes de tensão
    G_SUPER_ALTA = 1e12

    for comp in componentes:
        tipo = comp["tipo"].upper()
        n1 = comp["n1"]
        n2 = comp["n2"]
        val = comp["valor"]

        # --- Tratamento de Fontes de Tensão (CORRIGIDO) ---
        if tipo == 'V':
            # Apenas fontes aterradas (n2='0') são tratadas por este método simples
            if n1 != '0' and n2 == '0':
                fase = comp.get("fase", 0.0)
                fonte_v = val * np.exp(1j * np.deg2rad(fase))
                
                i = mapa_nos[n1]
                # Força o nó a ter a tensão da fonte (Técnica da Super Condutância)
                G[i, i] += G_SUPER_ALTA
                I[i] += fonte_v * G_SUPER_ALTA
            else:
                # Alerta para fontes não aterradas, que o método atual não suporta
                raise ValueError(f"Fonte de Tensão '{comp['nome']}' não está aterrada. Este método de análise não a suporta.")
            continue

        # --- Tratamento de Componentes Passivos ---
        y = 0
        if tipo == 'R':
            y = 1 / val
        elif tipo == 'L':
            y = 1 / (1j * w * val)
        elif tipo == 'C':
            y = 1j * w * val
        elif tipo == 'Z':
            y = 1 / val

        if y != 0:
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
    
    print("\n--- MATRIZ G (CORRIGIDA) ---")
    print(G)
    print("\n--- VETOR I (CORRIGIDO) ---")
    print(I)

    if np.linalg.matrix_rank(G) < len(G):
        raise ValueError("Matriz singular: circuito mal conectado ou sem referência.")

    V = np.linalg.solve(G, I)

    print("\n--- TENSÕES CALCULADAS (CORRIGIDAS) ---")
    print(V)

    correntes = []
    potencias = []

    for comp in componentes:
        tipo = comp["tipo"].upper()
        if tipo in ['R', 'L', 'C', 'Z']:
            nome = comp["nome"]
            n1 = comp["n1"]
            n2 = comp["n2"]
            val = comp["valor"]

            v1 = V[mapa_nos[n1]] if n1 != '0' else 0
            v2 = V[mapa_nos[n2]] if n2 != '0' else 0
            
            tensao_comp = v1 - v2

            if tipo == 'R': Z = val
            elif tipo == 'L': Z = 1j * w * val
            elif tipo == 'C': Z = 1 / (1j * w * val) if w * val != 0 else np.inf
            else: Z = val

            if Z == 0 or np.isinf(Z): continue

            corrente_comp = tensao_comp / Z
            correntes.append({"nome": f"I_{nome}", "valor": corrente_comp})
            
            S = tensao_comp * np.conj(corrente_comp)
            P = S.real
            Q = S.imag
            fp = P / abs(S) if abs(S) > 0 else 1.0
            
            potencias.append({
                "nome": comp["nome"],
                "S": S,
                "P": P,
                "Q": Q,
                "fp": fp
            })

    return V, mapa_nos, correntes, potencias