# core/analise.py

import numpy as np
from collections import defaultdict

def montar_matriz_anm(componentes, frequencia):
    w = 2 * np.pi * frequencia

    nos = set(['0'])
    fontes_v_indep = [c for c in componentes if c['tipo'].upper() == 'V']
    fontes_v_dep = [c for c in componentes if c['tipo'].upper() in ['E', 'H']]
    todas_fontes_v = fontes_v_indep + fontes_v_dep
    
    for comp in componentes:
        nos.add(comp["n1"])
        nos.add(comp["n2"])
        if 'nc1' in comp:
            nos.add(comp['nc1'])
            nos.add(comp['nc2'])

    nos_ordenados = sorted(list(nos - {'0'}))
    mapa_nos = {no: i for i, no in enumerate(nos_ordenados)}
    
    N = len(nos_ordenados)
    M = len(todas_fontes_v)

    A = np.zeros((N + M, N + M), dtype=complex)
    z = np.zeros(N + M, dtype=complex)
    mapa_indices_v = {fonte['nome']: i for i, fonte in enumerate(todas_fontes_v)}

    for comp in componentes:
        tipo = comp['tipo'].upper()
        n1, n2 = comp['n1'], comp['n2']
        i1 = mapa_nos.get(n1)
        i2 = mapa_nos.get(n2)

        if tipo in ['R', 'L', 'C', 'Z']:
            y = 0
            if tipo == 'R': y = 1 / comp['valor']
            elif tipo == 'L': y = 1 / (1j * w * comp['valor']) if comp['valor'] != 0 else np.inf
            elif tipo == 'C': y = 1j * w * comp['valor']
            else: y = 1 / comp['valor']
            
            if i1 is not None: A[i1, i1] += y
            if i2 is not None: A[i2, i2] += y
            if i1 is not None and i2 is not None:
                A[i1, i2] -= y; A[i2, i1] -= y
        
        elif tipo == 'G':
            nc1, nc2, ganho = mapa_nos.get(comp['nc1']), mapa_nos.get(comp['nc2']), comp['valor']
            if i1 is not None:
                if nc1 is not None: A[i1, nc1] -= ganho
                if nc2 is not None: A[i1, nc2] += ganho
            if i2 is not None:
                if nc1 is not None: A[i2, nc1] += ganho
                if nc2 is not None: A[i2, nc2] -= ganho

        elif tipo == 'F':
            ganho, comp_controle = comp['valor'], comp['controle']
            idx_v_controle = N + mapa_indices_v[comp_controle]
            if i1 is not None: A[i1, idx_v_controle] += ganho
            if i2 is not None: A[i2, idx_v_controle] -= ganho
    
    for k, fonte in enumerate(todas_fontes_v):
        tipo, nome = fonte['tipo'].upper(), fonte['nome']
        idx_p, idx_n = mapa_nos.get(fonte['n1']), mapa_nos.get(fonte['n2'])
        idx_matriz_m = N + k

        if idx_p is not None: A[idx_p, idx_matriz_m] = 1; A[idx_matriz_m, idx_p] = 1
        if idx_n is not None: A[idx_n, idx_matriz_m] = -1; A[idx_matriz_m, idx_n] = -1

        if tipo == 'V':
            fase_rad = np.deg2rad(fonte.get("fase", 0.0))
            z[idx_matriz_m] = fonte['valor'] * np.exp(1j * fase_rad)
        
        elif tipo == 'E':
            nc_p, nc_n, ganho = mapa_nos.get(fonte['nc1']), mapa_nos.get(fonte['nc2']), fonte['valor']
            if nc_p is not None: A[idx_matriz_m, nc_p] -= ganho
            if nc_n is not None: A[idx_matriz_m, nc_n] += ganho

        elif tipo == 'H':
            ganho, comp_controle = fonte['valor'], fonte['controle']
            idx_v_controle = N + mapa_indices_v[comp_controle]
            A[idx_matriz_m, idx_v_controle] -= ganho

    if np.linalg.matrix_rank(A) < A.shape[0]:
        raise ValueError("Matriz singular: circuito mal conectado ou com dependências inválidas.")
    
    solucao = np.linalg.solve(A, z)

    V_nodal = {no: solucao[idx] for no, idx in mapa_nos.items()}; V_nodal['0'] = 0
    I_fontes_v = {todas_fontes_v[k]['nome']: -solucao[N + k] for k in range(M)}
    
    correntes = {}
    potencias = {}
    tensoes_componentes = {}
    for comp in componentes:
        nome = comp['nome']
        tipo = comp['tipo'].upper()
        v1 = V_nodal.get(comp['n1'], 0)
        v2 = V_nodal.get(comp['n2'], 0)
        tensao_comp = v1 - v2
        tensoes_componentes[nome] = tensao_comp
        
        corrente_comp = 0
        if tipo in ['V', 'E', 'H']:
            corrente_comp = I_fontes_v.get(nome, 0)
        elif tipo == 'G':
            v_control_p = V_nodal.get(comp['nc1'], 0)
            v_control_n = V_nodal.get(comp['nc2'], 0)
            corrente_comp = comp['valor'] * (v_control_p - v_control_n)
        elif tipo == 'F':
            corrente_controle = I_fontes_v.get(comp['controle'], 0)
            corrente_comp = comp['valor'] * corrente_controle
        else:
            Z = 0
            if tipo == 'R': Z = comp['valor']
            elif tipo == 'L': Z = 1j * w * comp['valor']
            elif tipo == 'C': Z = 1 / (1j * w * comp['valor']) if (w * comp.get('valor', 0) != 0) else np.inf
            elif tipo == 'Z': Z = comp['valor']
            
            if Z != 0 and not np.isinf(Z):
                corrente_comp = tensao_comp / Z
        
        correntes[nome] = corrente_comp
        potencias[nome] = tensao_comp * np.conj(corrente_comp)

    Z_equivalente = None
    I_total = None
    if fontes_v_indep:
        fonte_principal = fontes_v_indep[0]
        I_total = correntes.get(fonte_principal['nome'])
        if I_total and abs(I_total) > 1e-12:
            fase_rad = np.deg2rad(fonte_principal.get("fase", 0.0))
            V_fonte = fonte_principal['valor'] * np.exp(1j * fase_rad)
            Z_equivalente = V_fonte / I_total
        else:
            Z_equivalente = complex(np.inf, np.inf)

    return V_nodal, correntes, potencias, tensoes_componentes, Z_equivalente, I_total