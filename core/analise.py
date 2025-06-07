# core/analise.py

import numpy as np

def montar_matriz_anm(componentes, frequencia):
    """
    Monta e resolve o sistema de equações lineares para análise de circuitos CA
    usando o método de Análise Nodal Modificada (ANM).

    Este método suporta qualquer topologia de circuito, incluindo fontes de tensão
    flutuantes.

    Retorna:
    - V (dict): Dicionário com as tensões nodais complexas. {'Nó': valor}
    - I (dict): Dicionário com as correntes complexas de todos os componentes. {'Comp': valor}
    - S (dict): Dicionário com as potências complexas de todos os componentes. {'Comp': valor}
    """
    w = 2 * np.pi * frequencia

    # Passo 1: Mapear todos os nós e fontes de tensão
    nos = set(['0'])
    fontes_v = [c for c in componentes if c['tipo'].upper() == 'V']
    
    for comp in componentes:
        nos.add(comp["n1"])
        nos.add(comp["n2"])

    # Nós ordenados, exceto o terra '0'
    nos_ordenados = sorted(list(nos - {'0'}))
    mapa_nos = {no: i for i, no in enumerate(nos_ordenados)}
    
    N = len(nos_ordenados)  # Número de nós (sem contar o terra)
    M = len(fontes_v)       # Número de fontes de tensão

    # Passo 2: Criar as matrizes da ANM: A*x = z
    # A matriz 'A' terá tamanho (N+M) x (N+M)
    # O vetor 'z' terá tamanho (N+M) x 1
    A = np.zeros((N + M, N + M), dtype=complex)
    z = np.zeros(N + M, dtype=complex)

    # Passo 3: Estampar os componentes passivos (R, L, C, Z) na matriz G
    for comp in componentes:
        tipo = comp['tipo'].upper()
        if tipo not in ['R', 'L', 'C', 'Z']:
            continue
            
        n1, n2, val = comp['n1'], comp['n2'], comp['valor']
        
        # Calcular admitância (y)
        if tipo == 'R': y = 1 / val
        elif tipo == 'L': y = 1 / (1j * w * val)
        elif tipo == 'C': y = 1j * w * val
        else: y = 1 / val

        # Estampar a admitância na submatriz G
        if n1 != '0':
            i = mapa_nos[n1]
            A[i, i] += y
        if n2 != '0':
            j = mapa_nos[n2]
            A[j, j] += y
        if n1 != '0' and n2 != '0':
            i, j = mapa_nos[n1], mapa_nos[n2]
            A[i, j] -= y
            A[j, i] -= y
            
    # Passo 4: Estampar as fontes de tensão nas matrizes B e C
    for k, fonte in enumerate(fontes_v):
        n_p, n_n = fonte['n1'], fonte['n2']
        
        # Estampar nas submatrizes B e C
        if n_p != '0':
            p_idx = mapa_nos[n_p]
            A[p_idx, N + k] = 1
            A[N + k, p_idx] = 1
        if n_n != '0':
            n_idx = mapa_nos[n_n]
            A[n_idx, N + k] = -1
            A[N + k, n_idx] = -1
            
        # Estampar o valor da fonte no vetor z
        fase_rad = np.deg2rad(fonte.get("fase", 0.0))
        z[N + k] = fonte['valor'] * np.exp(1j * fase_rad)

    # Passo 5: Resolver o sistema
    if np.linalg.matrix_rank(A) < A.shape[0]:
        raise ValueError("Matriz singular: circuito mal conectado, verifique as conexões e a referência (terra).")
    
    solucao = np.linalg.solve(A, z)

    # Passo 6: Extrair os resultados
    V_nodal = {no: solucao[idx] for no, idx in mapa_nos.items()}
    V_nodal['0'] = 0 # Adicionar o terra

    I_fontes_v = {fontes_v[k]['nome']: solucao[N + k] for k in range(M)}
    
    # Passo 7: Calcular correntes e potências de todos os componentes
    correntes = {}
    potencias = {}

    for comp in componentes:
        nome, tipo = comp['nome'], comp['tipo'].upper()
        n1, n2, val = comp['n1'], comp['n2'], comp['valor']
        
        v1 = V_nodal[n1]
        v2 = V_nodal[n2]
        tensao_comp = v1 - v2
        
        corrente_comp = 0
        if tipo == 'V':
            corrente_comp = I_fontes_v[nome]
        else:
            if tipo == 'R': Z = val
            elif tipo == 'L': Z = 1j * w * val
            elif tipo == 'C': Z = 1 / (1j * w * val) if w * val != 0 else np.inf
            else: Z = val
            
            if Z != 0 and not np.isinf(Z):
                corrente_comp = tensao_comp / Z

        correntes[nome] = corrente_comp
        
        # Potência: S = V * I*. Para fontes, a corrente I é a que sai do terminal positivo.
        # A ANM já nos dá essa corrente com a convenção correta.
        potencia_comp = tensao_comp * np.conj(corrente_comp)
        potencias[nome] = potencia_comp
        
    return V_nodal, correntes, potencias