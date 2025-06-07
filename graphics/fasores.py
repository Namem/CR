# graphics/fasores.py

import matplotlib.pyplot as plt
import numpy as np

def plotar_fasores(dados, titulo="Diagrama Fasorial"):
    """
    dados = lista de dicts com: {"nome": str, "valor": complex}
    """
    fig, ax = plt.subplots()
    ax.set_title(titulo)
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')

    for dado in dados:
        nome = dado["nome"]
        val = dado["valor"]
        ax.arrow(0, 0, val.real, val.imag, head_width=0.05, length_includes_head=True)
        ax.text(val.real * 1.1, val.imag * 1.1, nome)

    ax.grid(True)
    ax.set_xlabel("Re")
    ax.set_ylabel("Im")
    plt.show()
