# graphics/fasores.py

import matplotlib.pyplot as plt
import numpy as np

def plotar_fasores(ax, dados, titulo="Diagrama Fasorial"):
    """
    Plota fasores em um eixo (ax) do Matplotlib.
    dados = lista de dicts com: {"nome": str, "valor": complex}
    """
    ax.clear()  # Limpa o eixo antes de desenhar
    ax.set_title(titulo)
    ax.grid(True)
    ax.set_xlabel("Re")
    ax.set_ylabel("Im")
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)
    
    # Normalização para melhor visualização
    max_val = max((abs(d["valor"]) for d in dados), default=1.0)
    fator = 1.0 / max_val if max_val > 0 else 1.0

    for d in dados:
        val_norm = d["valor"] * fator
        ax.arrow(0, 0, val_norm.real, val_norm.imag, head_width=0.05, 
                 length_includes_head=True, label=d["nome"])
        ax.text(val_norm.real * 1.1, val_norm.imag * 1.1, d["nome"])

    ax.set_aspect('equal', adjustable='box')