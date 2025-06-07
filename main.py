from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem
)
import sys

from netlist_parser import parser
from core import analise
from interface.canvas import MplCanvas
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choque de Realidade - Analisador CA")
        self.setGeometry(100, 100, 1000, 700)

        self.componentes = []
        self.frequencia = 60
        self.tensoes = []
        self.correntes = []

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Aba Netlist
        self.tab_netlist = QWidget()
        self.tabs.addTab(self.tab_netlist, "📝 Netlist")
        self.setup_netlist_tab()

        # Aba Resultados
        self.tab_resultados = QWidget()
        self.tabs.addTab(self.tab_resultados, "⚡ Resultados")
        self.setup_resultados_tab()

        # Aba Fasores
        self.tab_fasores = QWidget()
        self.tabs.addTab(self.tab_fasores, "📊 Fasores")
        self.fasor_canvas = MplCanvas()
        layout_fasor = QVBoxLayout()
        layout_fasor.addWidget(self.fasor_canvas)
        self.tab_fasores.setLayout(layout_fasor)

        # Aba Ondas
        self.tab_ondas = QWidget()
        self.tabs.addTab(self.tab_ondas, "🌊 Ondas")
        self.onda_canvas = MplCanvas()
        layout_ondas = QVBoxLayout()
        layout_ondas.addWidget(self.onda_canvas)
        self.tab_ondas.setLayout(layout_ondas)

    def setup_netlist_tab(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Digite sua netlist estilo SPICE:\nExemplo:\nV1 n1 0 AC 120 0\nR1 n1 n2 50\n..."
        )
        layout.addWidget(self.text_edit)

        btn_analisar = QPushButton("⚡ Analisar Circuito")
        btn_analisar.clicked.connect(self.analisar)
        layout.addWidget(btn_analisar)

        self.tab_netlist.setLayout(layout)

    def setup_resultados_tab(self):
        layout = QVBoxLayout()

        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)

        self.tab_resultados.setLayout(layout)

    def analisar(self):
        texto = self.text_edit.toPlainText()
        if not texto.strip():
            QMessageBox.warning(self, "Aviso", "Digite uma netlist válida.")
            return

        try:
            linhas = texto.strip().split('\n')
            self.componentes = parser.parse_netlist_linhas(linhas)
            V, mapa_nos, correntes = analise.montar_matriz(self.componentes, self.frequencia)
            self.tensoes = [{"nome": f"V_{no}", "valor": V[idx]} for no, idx in mapa_nos.items()]
            self.correntes = correntes
            todos = self.tensoes + self.correntes

            self.atualizar_tabela()
            self.plotar_fasores(todos)
            self.plotar_ondas(todos)

            self.tabs.setCurrentIndex(1)  # vai direto para aba de resultados

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha na análise:\n{e}")

    def atualizar_tabela(self):
        todos = self.tensoes + self.correntes
        self.tabela.setRowCount(len(todos))
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["Nome", "Valor (Polar)", "Valor (Retangular)"])

        for i, comp in enumerate(todos):
            nome = comp["nome"]
            val = comp["valor"]
            polar = f"{abs(val):.2f} ∠ {np.angle(val, deg=True):.2f}°"
            ret = f"{val.real:.2f} + j{val.imag:.2f}"
            self.tabela.setItem(i, 0, QTableWidgetItem(nome))
            self.tabela.setItem(i, 1, QTableWidgetItem(polar))
            self.tabela.setItem(i, 2, QTableWidgetItem(ret))

    def plotar_fasores(self, dados):
        ax = self.fasor_canvas.ax
        self.fasor_canvas.clear()
        ax.set_title("Fasores de Tensões e Correntes")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')

        max_val = max(abs(d["valor"]) for d in dados)
        fator = 1.0 / max_val if max_val > 0 else 1.0

        for d in dados:
            val = d["valor"] * fator
            ax.arrow(0, 0, val.real, val.imag, head_width=0.05, length_includes_head=True)
            ax.text(val.real * 1.1, val.imag * 1.1, d["nome"])

        ax.grid(True)
        ax.set_xlabel("Re")
        ax.set_ylabel("Im")
        self.fasor_canvas.draw()

    def plotar_ondas(self, dados, ciclos=2):
        t = np.linspace(0, ciclos / self.frequencia, 1000)
        ax = self.onda_canvas.ax
        self.onda_canvas.clear()

        for d in dados:
            val = d["valor"]
            amp = abs(val)
            fase = np.angle(val)
            sinal = amp * np.cos(2 * np.pi * self.frequencia * t + fase)
            ax.plot(t, sinal, label=d["nome"])

        ax.set_title("Ondas Senoidais de Tensões e Correntes")
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        ax.grid(True)
        self.onda_canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())
