from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout
)
import sys
import numpy as np

from netlist_parser import parser
from core import analise
from interface.canvas import MplCanvas


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

        # Abas
        self.tab_netlist = QWidget()
        self.tab_resultados = QWidget()
        self.tab_fasores = QWidget()
        self.tab_ondas = QWidget()

        self.tabs.addTab(self.tab_netlist, "📝 Netlist")
        self.tabs.addTab(self.tab_resultados, "⚡ Resultados")
        self.tabs.addTab(self.tab_fasores, "📊 Fasores")
        self.tabs.addTab(self.tab_ondas, "🌊 Ondas")

        self.setup_netlist_tab()
        self.setup_resultados_tab()

        self.fasor_canvas = MplCanvas()
        layout_fasor = QVBoxLayout()
        layout_fasor.addWidget(self.fasor_canvas)
        self.tab_fasores.setLayout(layout_fasor)

        self.onda_canvas = MplCanvas()
        layout_ondas = QVBoxLayout()
        layout_ondas.addWidget(self.onda_canvas)
        self.tab_ondas.setLayout(layout_ondas)

    def setup_netlist_tab(self):
        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(
            "Digite sua netlist estilo SPICE:\nExemplo:\nV1 A 0 AC 220 0\nR1 A B 50\n..."
        )
        layout.addWidget(self.text_edit)

        btn_analisar = QPushButton("⚡ Analisar Circuito")
        btn_analisar.clicked.connect(self.analisar)
        layout.addWidget(btn_analisar)

        layout.addWidget(QLabel("Adicionar Motor Trifásico"))

        form = QFormLayout()
        self.tipo_motor = QComboBox()
        self.tipo_motor.addItems(["Estrela (Y)", "Triângulo (Δ)"])

        self.noA = QLineEdit("A")
        self.noB = QLineEdit("B")
        self.noC = QLineEdit("C")
        self.noN = QLineEdit("N")
        self.potencia = QLineEdit("3000")
        self.fp = QLineEdit("0.9")

        form.addRow("Tipo de Ligação:", self.tipo_motor)
        form.addRow("Nó A:", self.noA)
        form.addRow("Nó B:", self.noB)
        form.addRow("Nó C:", self.noC)
        form.addRow("Nó Neutro (Y apenas):", self.noN)
        form.addRow("Potência (W):", self.potencia)
        form.addRow("Fator de Potência:", self.fp)

        layout.addLayout(form)

        btn_inserir_motor = QPushButton("➕ Inserir Motor na Netlist")
        btn_inserir_motor.clicked.connect(self.inserir_motor_netlist)
        layout.addWidget(btn_inserir_motor)

        self.tab_netlist.setLayout(layout)

    def inserir_motor_netlist(self):
        tipo = self.tipo_motor.currentText()
        a = self.noA.text().strip()
        b = self.noB.text().strip()
        c = self.noC.text().strip()
        n = self.noN.text().strip()
        p = self.potencia.text().strip()
        fp = self.fp.text().strip()
        nome_motor = f"M{np.random.randint(100,999)}"

        if tipo.startswith("Estrela"):
            motor_line = f"MOTOR_Y {nome_motor} {a} {b} {c} {n} {p} {fp}"
        else:
            motor_line = f"MOTOR_D {nome_motor} {a} {b} {c} {p} {fp}"

        # Fontes trifásicas
        fontes = [
            f"V1 {a} 0 AC 220 0",
            f"V2 {b} 0 AC 220 -120",
            f"V3 {c} 0 AC 220 120",
        ]

        extra = []
        if tipo.startswith("Estrela"):
            extra.append(f"RNEUTRO {n} 0 0.001")

        texto_atual = self.text_edit.toPlainText().strip().splitlines()
        linhas_existentes = set(l.strip().split()[0] for l in texto_atual)

        novas_linhas = []
        for v in fontes:
            if v.split()[0] not in linhas_existentes:
                novas_linhas.append(v)

        novas_linhas.append(motor_line)
        novas_linhas += extra

        texto_final = "\n".join(texto_atual + novas_linhas)
        self.text_edit.setText(texto_final)

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
            self.tabs.setCurrentIndex(1)

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
