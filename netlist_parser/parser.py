# netlist_parser/parser.py

import math
import re

class NetlistParseError(Exception):
    def __init__(self, message, line_number):
        self.message = message
        self.line_number = line_number
        super().__init__(f"Linha {line_number}: {message}")

def parse_valor_com_unidade(valor_str):
    valor_str = valor_str.lower()
    unidades = {'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3, 'meg': 1e6, 'g': 1e9, 't': 1e12}
    match = re.match(r"^(-?\d+\.?\d*)([a-z]+)?$", valor_str) # Unidade opcional
    if match:
        valor_numerico, unidade = match.groups()
        if unidade:
            multiplicador = unidades.get(unidade)
            if multiplicador:
                return float(valor_numerico) * multiplicador
            else:
                raise ValueError(f"Unidade desconhecida: '{unidade}'")
        return float(valor_numerico)
    raise ValueError(f"Formato de número inválido: '{valor_str}'")

def parse_netlist_linhas(linhas):
    componentes = []
    for i, linha in enumerate(linhas):
        linha_numero = i + 1
        linha_limpa = linha.strip()
        if not linha_limpa or linha_limpa.startswith("*"): continue

        tokens = linha_limpa.split()
        if len(tokens) < 4:
            raise NetlistParseError("Linha incompleta.", linha_numero)

        nome_comp = tokens[0]
        tipo_comp = nome_comp[0].upper()
        
        try:
            # --- NOVA LÓGICA PARA FONTES DEPENDENTES (E, G, F, H) ---
            if tipo_comp in ['E', 'G', 'F', 'H']:
                if len(tokens) != 6: raise NetlistParseError(f"Fonte dependente {tipo_comp} requer 6 tokens.", linha_numero)
                n_pos, n_neg = tokens[1], tokens[2]
                nc_pos, nc_neg = tokens[3], tokens[4]
                ganho = parse_valor_com_unidade(tokens[5])
                
                # Para fontes F e H, o controle é uma fonte V de 0V para medir a corrente
                comp_controle = None
                if tipo_comp in ['F', 'H']:
                    comp_controle = f"Vctrl_{nome_comp}"

                componentes.append({
                    "tipo": tipo_comp, "nome": nome_comp, "n1": n_pos, "n2": n_neg,
                    "nc1": nc_pos, "nc2": nc_neg, "valor": ganho, "controle": comp_controle
                })

                # Se for F ou H, adiciona a fonte "amperímetro" de 0V
                if comp_controle:
                    componentes.append({
                        "tipo": "V", "nome": comp_controle, "n1": nc_pos, "n2": nc_neg,
                        "valor": 0, "fase": 0
                    })

            elif len(tokens) > 3 and tokens[3].upper() == "AC":
                if len(tokens) < 5: raise NetlistParseError("Fonte AC requer um valor de magnitude.", linha_numero)
                n1, n2 = tokens[1], tokens[2]
                valor = parse_valor_com_unidade(tokens[4])
                fase = parse_valor_com_unidade(tokens[5]) if len(tokens) > 5 else 0.0
                componentes.append({
                    "tipo": "V", "nome": nome_comp, "n1": n1, "n2": n2, "valor": valor, "fase": fase
                })
            else:
                n1, n2 = tokens[1], tokens[2]
                if len(tokens) > 4:
                    real_part = parse_valor_com_unidade(tokens[3])
                    imag_part = parse_valor_com_unidade(tokens[4])
                    valor = complex(real_part, imag_part)
                else:
                    valor = parse_valor_com_unidade(tokens[3])
                
                componentes.append({
                    "tipo": tipo_comp, "nome": nome_comp, "n1": n1, "n2": n2, "valor": valor
                })
        except (ValueError, IndexError) as e:
            raise NetlistParseError(f"Erro ao processar valor: {e}", linha_numero)

    return componentes

def calcular_impedancia_motor(potencia_total_ativa, fp, ligacao='Y', tensao_fase=220):
    p_fase = potencia_total_ativa / 3; s_fase = p_fase / fp
    if s_fase == 0: return complex(1e12, 0)
    theta = math.acos(fp); z_mod = (tensao_fase**2) / s_fase
    return z_mod * complex(math.cos(theta), math.sin(theta))