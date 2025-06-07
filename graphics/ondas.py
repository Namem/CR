# graphics/ondas.py

import matplotlib.pyplot as plt
import numpy as np

def plotar_ondas(ax, dados, f=60, ciclos=2, titulo="Formas de Onda"):
    """
    Plota formas de onda em um eixo (ax) do Matplotlib.
    dados = lista de dicts com: {"nome": str, "valor": complex}
    """
    ax.clear() # Limpa o eixo antes de desenhar
    t = np.linspace(0, ciclos / f, 1000)

    for dado in dados:
        nome = dado["nome"]
        val = dado["valor"]
        amplitude = abs(val)
        fase = np.angle(val)
        onda = amplitude * np.cos(2 * np.pi * f * t + fase)
        ax.plot(t, onda, label=nome)

    ax.set_title(titulo)
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    ax.legend()