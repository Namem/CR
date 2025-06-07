# graphics/ondas.py

import matplotlib.pyplot as plt
import numpy as np

def plotar_ondas(dados, f=60, ciclos=2):
    """
    dados = lista de dicts com: {"nome": str, "valor": complex}
    """
    t = np.linspace(0, ciclos / f, 1000)

    plt.figure()
    for dado in dados:
        nome = dado["nome"]
        val = dado["valor"]
        amplitude = abs(val)
        fase = np.angle(val)
        onda = amplitude * np.cos(2 * np.pi * f * t + fase)
        plt.plot(t, onda, label=nome)

    plt.title("Diagrama de Ondas")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.show()
