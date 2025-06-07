# netlist_parser/parser.py

import math
import re

# --- NOVA FUNÇÃO ---
def parse_valor_com_unidade(valor_str):
    """
    Interpreta um valor string que pode conter um prefixo de unidade do SI.
    Ex: '10k' -> 10000.0, '100n' -> 1e-7
    """
    valor_str = valor_str.lower()
    
    unidades = {
        'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3,
        'k': 1e3, 'meg': 1e6, 'g': 1e9, 't': 1e12
    }
    
    # Tenta encontrar uma unidade no final da string
    match = re.match(r"^(-?\d+\.?\d*)([a-z]+)$", valor_str)
    
    if match:
        valor_numerico, unidade = match.groups()
        multiplicador = unidades.get(unidade)
        
        if multiplicador:
            return float(valor_numerico) * multiplicador
        else:
            # Se a unidade não for reconhecida, lança um erro
            raise ValueError(f"Unidade desconhecida: '{unidade}' em '{valor_str}'")
    else:
        # Se não houver unidade, converte para float diretamente
        return float(valor_str)

def parse_netlist_linhas(linhas):
    componentes = []

    for linha in linhas:
        linha_limpa = linha.strip()
        if not linha_limpa or linha_limpa.startswith("*"):
            continue

        tokens = linha_limpa.split()
        nome_comp = tokens[0]
        tipo_comp = nome_comp[0].upper()

        if len(tokens) > 3 and tokens[3].upper() == "AC":
            n1, n2 = tokens[1], tokens[2]
            # Usa a nova função para interpretar os valores de magnitude e fase
            valor = parse_valor_com_unidade(tokens[4])
            fase = parse_valor_com_unidade(tokens[5]) if len(tokens) > 5 else 0.0
            componentes.append({
                "tipo": "V", "nome": nome_comp, "n1": n1, "n2": n2, "valor": valor, "fase": fase
            })
        else:
            n1, n2 = tokens[1], tokens[2]
            
            # --- CORREÇÃO APLICADA AQUI ---
            if len(tokens) > 4:
                # Impedância complexa: Z N1 N2 REAL IMAG
                try:
                    # Usa a nova função para cada parte
                    real_part = parse_valor_com_unidade(tokens[3])
                    imag_part = parse_valor_com_unidade(tokens[4])
                    valor = complex(real_part, imag_part)
                except ValueError as e:
                    raise ValueError(f"Valor de impedância inválido para {nome_comp}: {e}")
            else:
                # Componente com valor real: R N1 N2 VALOR
                try:
                    # Usa a nova função para o valor
                    valor = parse_valor_com_unidade(tokens[3])
                except ValueError as e:
                    raise ValueError(f"Valor inválido para {nome_comp}: {e}")
            
            componentes.append({
                "tipo": tipo_comp,
                "nome": nome_comp,
                "n1": n1,
                "n2": n2,
                "valor": valor
            })

    return componentes

def calcular_impedancia_motor(potencia_total_ativa, fp, ligacao='Y', tensao_fase=220):
    # (Esta função permanece a mesma da versão anterior)
    p_fase = potencia_total_ativa / 3
    s_fase = p_fase / fp
    if s_fase == 0:
        return complex(1e12, 0)
    theta = math.acos(fp)
    z_mod = (tensao_fase**2) / s_fase
    return z_mod * complex(math.cos(theta), math.sin(theta))