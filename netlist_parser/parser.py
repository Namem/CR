# netlist_parser/parser.py

import math

def parse_netlist_linhas(linhas):
    componentes = []

    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa or linha_limpa.startswith("*"):
            continue

        tokens = linha_limpa.split()
        nome_comp = tokens[0]
        tipo_comp = nome_comp[0].upper()

        # Tratamento especial para fontes AC e motores (que usam sintaxe diferente)
        # O resto é tratado como um componente genérico R, L, C, ou Z
        if len(tokens) > 3 and tokens[3].upper() == "AC":
            # Fonte de Tensão AC: V1 A 0 AC 220 0
            n1, n2 = tokens[1], tokens[2]
            valor = float(tokens[4])
            fase = float(tokens[5]) if len(tokens) > 5 else 0.0
            componentes.append({
                "tipo": "V", "nome": nome_comp, "n1": n1, "n2": n2, "valor": valor, "fase": fase
            })
        else:
            # Componentes R, L, C ou Z (com valor real ou complexo)
            n1, n2 = tokens[1], tokens[2]
            
            # --- CORREÇÃO DO BUG AQUI ---
            # Verifica se há uma parte imaginária para a impedância
            if len(tokens) > 4:
                # É uma impedância complexa: Z_NOME N1 N2 REAL IMAG
                try:
                    real_part = float(tokens[3])
                    imag_part = float(tokens[4])
                    valor = complex(real_part, imag_part)
                except ValueError:
                    raise ValueError(f"Valor de impedância inválido para {nome_comp}: {tokens[3]} {tokens[4]}")
            else:
                # É um componente com valor real: R_NOME N1 N2 VALOR
                try:
                    valor = float(tokens[3])
                except ValueError:
                    raise ValueError(f"Valor inválido para {nome_comp}: {tokens[3]}")
            
            componentes.append({
                "tipo": tipo_comp,
                "nome": nome_comp,
                "n1": n1,
                "n2": n2,
                "valor": valor
            })

    return componentes


def calcular_impedancia_motor(potencia_total_ativa, fp, ligacao='Y', tensao_fase=220):
    """
    Calcula a impedância complexa equivalente por fase de um motor.
    potencia_total_ativa: Potência ativa total (P) em Watts.
    fp: Fator de potência (cosseno do ângulo).
    """
    # Potência ativa por fase
    p_fase = potencia_total_ativa / 3
    
    # Potência aparente por fase
    s_fase = p_fase / fp
    
    if s_fase == 0:
        return complex(1e12, 0) # Retorna uma impedância muito alta para evitar divisão por zero

    # Ângulo da impedância
    theta = math.acos(fp)
    
    # Magnitude da impedância por fase
    z_mod = (tensao_fase**2) / s_fase

    # Retorna o número complexo da impedância
    return z_mod * complex(math.cos(theta), math.sin(theta))