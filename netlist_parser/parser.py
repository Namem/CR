# netlist_parser/parser.py

import math

def parse_netlist_linhas(linhas):
    componentes = []

    for linha in linhas:
        if linha.strip() == "" or linha.startswith("*"):
            continue

        tokens = linha.split()
        tipo = tokens[0].upper()

        if tipo == "MOTOR_Y":
            nome = tokens[1]
            a, b, c, neutro = tokens[2], tokens[3], tokens[4], tokens[5]
            potencia = float(tokens[6])
            fp = float(tokens[7])

            z = calcular_impedancia_motor(potencia, fp, ligacao='Y')

            # Três impedâncias: A-Neutro, B-Neutro, C-Neutro
            componentes.append({"tipo": "Z", "nome": f"{nome}_A", "n1": a, "n2": neutro, "valor": z})
            componentes.append({"tipo": "Z", "nome": f"{nome}_B", "n1": b, "n2": neutro, "valor": z})
            componentes.append({"tipo": "Z", "nome": f"{nome}_C", "n1": c, "n2": neutro, "valor": z})

        elif tipo == "MOTOR_D":
            nome = tokens[1]
            a, b, c = tokens[2], tokens[3], tokens[4]
            potencia = float(tokens[5])
            fp = float(tokens[6])

            z = calcular_impedancia_motor(potencia, fp, ligacao='D')

            # Três impedâncias entre fases: AB, BC, CA
            componentes.append({"tipo": "Z", "nome": f"{nome}_AB", "n1": a, "n2": b, "valor": z})
            componentes.append({"tipo": "Z", "nome": f"{nome}_BC", "n1": b, "n2": c, "valor": z})
            componentes.append({"tipo": "Z", "nome": f"{nome}_CA", "n1": c, "n2": a, "valor": z})

        elif tokens[0][0].upper() == 'V' and tokens[3].upper() == "AC":
            nome = tokens[0]
            n1, n2 = tokens[1], tokens[2]
            valor = float(tokens[4])
            fase = float(tokens[5]) if len(tokens) > 5 else 0.0
            componentes.append({
                "tipo": "V", "nome": nome, "n1": n1, "n2": n2, "valor": valor, "fase": fase
            })

        else:
            nome = tokens[0]
            n1, n2 = tokens[1], tokens[2]
            valor = float(tokens[3])
            componentes.append({
                "tipo": tokens[0][0].upper(),
                "nome": nome,
                "n1": n1,
                "n2": n2,
                "valor": valor
            })

    return componentes


def calcular_impedancia_motor(potencia_total, fp, ligacao='Y', tensao_fase=220, freq=60):
    """
    Estima a impedância complexa equivalente por fase de um motor
    """
    s = potencia_total / 3  # potência por fase
    ang = math.acos(fp)
    p = s * fp
    q = s * math.sin(ang)
    v = tensao_fase

    z_mod = v**2 / s
    theta = math.atan2(q, p)

    return z_mod * complex(math.cos(theta), math.sin(theta))
