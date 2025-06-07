def parse_netlist_linhas(linhas):
    """
    Mesma função de parse_netlist, mas a partir de uma lista de strings (linhas).
    """
    componentes = []

    for linha in linhas:
        if linha.strip() == "" or linha.startswith("*"):
            continue

        tokens = linha.split()
        tipo = tokens[0][0].upper()
        nome = tokens[0]
        no1 = tokens[1]
        no2 = tokens[2]

        if tipo == 'V' and tokens[3].upper() == "AC":
            valor = float(tokens[4])
            fase = float(tokens[5]) if len(tokens) > 5 else 0.0
            componentes.append({
                "tipo": tipo,
                "nome": nome,
                "n1": no1,
                "n2": no2,
                "valor": valor,
                "fase": fase
            })
        else:
            valor = float(tokens[3])
            componentes.append({
                "tipo": tipo,
                "nome": nome,
                "n1": no1,
                "n2": no2,
                "valor": valor
            })

    return componentes
