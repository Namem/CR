# core/analise.py

import numpy as np
from collections import defaultdict

def montar_matriz_anm(componentes, frequencia):
    """
    Monta e resolve o sistema de equações lineares para análise de circuitos CA
    usando o método de Análise Nodal Modificada (ANM), com suporte a fontes dependentes.
    """
    w = 2 * np.pi * frequencia

    # Passo 1: Mapear nós e fontes de tensão (dependentes ou independentes)
    nos = set(['0'])
    fontes_v_indep = [c for c in componentes if c['tipo'].upper() == 'V']
    # Fontes de tensão controladas (E e H) também são tratadas como fontes de tensão na matriz
    fontes_v_dep = [c for c in componentes if c['tipo'].upper() in ['E', 'H']]
    todas_fontes_v = fontes_v_indep + fontes_v_dep
    
    for comp in componentes:
        nos.add(comp["n1"])
        nos.add(comp["n2"])
        # Fontes dependentes podem ter nós de controle
        if 'nc1' in comp:
            nos.add(comp['nc1'])
            nos.add(comp['nc2'])

    nos_ordenados = sorted(list(nos - {'0'}))
    mapa_nos = {no: i for i, no in enumerate(nos_ordenados)}
    
    N = len(nos_ordenados)
    M = len(todas_fontes_v)

    # Passo 2: Criar as matrizes da ANM
    A = np.zeros((N + M, N + M), dtype=complex)
    z = np.zeros(N + M, dtype=complex)

    # Dicionário para mapear nomes de fontes de tensão para seus índices na matriz (colunas M)
    mapa_indices_v = {fonte['nome']: i for i, fonte in enumerate(todas_fontes_v)}

    # Passo 3: Estampar componentes
    for comp in componentes:
        tipo = comp['tipo'].upper()
        n1, n2 = comp['n1'], comp['n2']
        i1 = mapa_nos.get(n1)
        i2 = mapa_nos.get(n2)

        if tipo in ['R', 'L', 'C', 'Z']:
            if tipo == 'R': y = 1 / comp['valor']
            elif tipo == 'L': y = 1 / (1j * w * comp['valor'])
            elif tipo == 'C': y = 1j * w * comp['valor']
            else: y = 1 / comp['valor']
            
            if i1 is not None: A[i1, i1] += y
            if i2 is not None: A[i2, i2] += y
            if i1 is not None and i2 is not None:
                A[i1, i2] -= y; A[i2, i1] -= y
        
        # --- NOVA LÓGICA PARA FONTES DEPENDENTES ---
        elif tipo == 'G': # VCCS: Fonte de Corrente Controlada por Tensão
            nc1, nc2, ganho = mapa_nos.get(comp['nc1']), mapa_nos.get(comp['nc2']), comp['valor']
            if i1 is not None:
                if nc1 is not None: A[i1, nc1] += ganho
                if nc2 is not None: A[i1, nc2] -= ganho
            if i2 is not None:
                if nc1 is not None: A[i2, nc1] -= ganho
                if nc2 is not None: A[i2, nc2] += ganho

        elif tipo == 'F': # CCCS: Fonte de Corrente Controlada por Corrente
            ganho, comp_controle = comp['valor'], comp['controle']
            idx_v_controle = N + mapa_indices_v[comp_controle]
            if i1 is not None: A[i1, idx_v_controle] += ganho
            if i2 is not None: A[i2, idx_v_controle] -= ganho
    
    # Passo 4: Estampar todas as fontes de tensão (independentes e dependentes)
    for k, fonte in enumerate(todas_fontes_v):
        tipo, nome = fonte['tipo'].upper(), fonte['nome']
        n_p, n_n = fonte['n1'], fonte['n2']
        idx_p, idx_n = mapa_nos.get(n_p), mapa_nos.get(n_n)
        
        idx_matriz_m = N + k

        if idx_p is not None: A[idx_p, idx_matriz_m] = 1; A[idx_matriz_m, idx_p] = 1
        if idx_n is not None: A[idx_n, idx_matriz_m] = -1; A[idx_matriz_m, idx_n] = -1

        if tipo == 'V':
            fase_rad = np.deg2rad(fonte.get("fase", 0.0))
            z[idx_matriz_m] = fonte['valor'] * np.exp(1j * fase_rad)
        
        elif tipo == 'E': # VCVS: Fonte de Tensão Controlada por Tensão
            nc_p, nc_n, ganho = mapa_nos.get(fonte['nc1']), mapa_nos.get(fonte['nc2']), fonte['valor']
            if nc_p is not None: A[idx_matriz_m, nc_p] -= ganho
            if nc_n is not None: A[idx_matriz_m, nc_n] += ganho

        elif tipo == 'H': # CCVS: Fonte de Tensão Controlada por Corrente
            ganho, comp_controle = fonte['valor'], fonte['controle']
            idx_v_controle = N + mapa_indices_v[comp_controle]
            A[idx_matriz_m, idx_v_controle] -= ganho

    # Passo 5: Resolver e extrair resultados (mesma lógica de antes)
    if np.linalg.matrix_rank(A) < A.shape[0]:
        raise ValueError("Matriz singular: circuito mal conectado ou com dependências inválidas.")
    
    solucao = np.linalg.solve(A, z)

    V_nodal = {no: solucao[idx] for no, idx in mapa_nos.items()}; V_nodal['0'] = 0
    I_fontes_v = {todas_fontes_v[k]['nome']: solucao[N + k] for k in range(M)}
    
    correntes = {}; potencias = {}
    for comp in componentes:
        nome, tipo = comp['nome'], comp['tipo'].upper()
        v1, v2 = V_nodal[comp['n1']], V_nodal[comp['n2']]
        tensao_comp = v1 - v2
        
        corrente_comp = 0
        if tipo in ['V', 'E', 'H']:
            corrente_comp = I_fontes_v[nome]
        elif tipo in ['F', 'G']: # Corrente já é definida pela equação de controle
             # O cálculo da corrente real para F e G é mais complexo, por ora pegamos a potência
             pass 
        else:
            if tipo == 'R': Z = comp['valor']
            elif tipo == 'L': Z = 1j * w * comp['valor']
            elif tipo == 'C': Z = 1 / (1j * w * comp['valor']) if w * comp['valor'] != 0 else np.inf
            else: Z = comp['valor']
            if Z != 0 and not np.isinf(Z): corrente_comp = tensao_comp / Z
        
        correntes[nome] = corrente_comp
        potencias[nome] = tensao_comp * np.conj(corrente_comp)
        
    return V_nodal, correntes, potencias