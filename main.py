# main.py

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QHeaderView, QFileDialog,
    QListWidget, QListWidgetItem
)
from PySide6.QtGui import QAction, QColor
from PySide6.QtCore import Qt
import sys
import numpy as np
import csv

# Importe os módulos do projeto
from netlist_parser import parser
from core import analise
from interface.canvas import MplCanvas
from graphics import fasores, ondas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choque de Realidade - Analisador CA")
        self.setGeometry(100, 100, 1100, 750)

        # (O resto do __init__ e outras funções permanecem os mesmos)
        self._create_menu_bar()
        self.componentes = []
        self.frequencia = 60
        self.tensoes = {}
        self.correntes = {}
        self.potencias = {}
        self.todos_sinais = []
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
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
        self.setup_graficos_tab(self.tab_fasores, "fasores")
        self.setup_graficos_tab(self.tab_ondas, "ondas")

    # --- MÉTODO ATUALIZADO PARA O LAYOUT FINAL DA TABELA ---
    def atualizar_tabela(self):
        self.tabela.clear()
        self.tabela.setRowCount(0)
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "Agrupamento", "Grandeza", "Valor Polar", "Valor Retangular", 
            "Potência Ativa (P)", "Potência Reativa (Q)", "Fator de Potência (FP)"
        ])
        
        # --- Helpers para adicionar linhas ---
        def add_separator_row(text):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor(60, 60, 60))
            self.tabela.setItem(row, 0, item)
            self.tabela.setSpan(row, 0, 1, self.tabela.columnCount())

        def add_data_row(agrupamento, grandeza, valor_complexo):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(agrupamento))
            self.tabela.setItem(row, 1, QTableWidgetItem(grandeza))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{abs(valor_complexo):.2f} ∠ {np.angle(valor_complexo, deg=True):.2f}°"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{valor_complexo.real:.2f} + j({valor_complexo.imag:.2f})"))

        def add_power_row(agrupamento, grandeza, S):
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            P, Q = S.real, S.imag
            fp_val = P / abs(S) if abs(S) > 1e-9 else 1.0
            fp_status = "adiantado" if Q < 0 else "atrasado"
            
            self.tabela.setItem(row, 0, QTableWidgetItem(agrupamento))
            self.tabela.setItem(row, 1, QTableWidgetItem(grandeza))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{abs(S):.2f} VA ∠ {np.angle(S, deg=True):.2f}°"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{P:.2f} + j({Q:.2f})"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"{P:.2f} W"))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"{Q:.2f} VAR"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{abs(fp_val):.3f} {fp_status}"))

        # 1. Mostra as Tensões Nodais
        add_separator_row("--- Tensões Nodais ---")
        for nome, valor in sorted(self.tensoes.items()):
            if nome == '0': continue
            add_data_row(f"Nó '{nome}'", f"Tensão V({nome})", valor)

        # 2. Mostra os dados agrupados por componente
        for comp in self.componentes:
            nome = comp['nome']
            add_separator_row(f"--- Componente: {nome} ---")
            add_data_row(nome, f"Corrente I({nome})", self.correntes[nome])
            add_power_row(nome, f"Potência S({nome})", self.potencias[nome])

        # 3. Adiciona o resumo trifásico se aplicável
        motores_agrupados = {}
        for comp in self.componentes:
            if comp['nome'].startswith('Z_M'):
                partes = comp['nome'].split('_'); nome_motor = partes[1]
                if nome_motor not in motores_agrupados: motores_agrupados[nome_motor] = []
                motores_agrupados[nome_motor].append(comp)
        for nome_motor, comps_motor in motores_agrupados.items():
            if len(comps_motor) == 3: self.adicionar_resumo_trifasico_agrupado(nome_motor, comps_motor)

        self.tabela.resizeColumnsToContents()

    def adicionar_resumo_trifasico_agrupado(self, nome_motor, comps_motor):
        # (Lógica interna adaptada para o novo layout)
        def add_separator_row(text):
            row = self.tabela.rowCount(); self.tabela.insertRow(row)
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor(60, 60, 60)); self.tabela.setItem(row, 0, item)
            self.tabela.setSpan(row, 0, 1, self.tabela.columnCount())

        def add_data_row(agrupamento, grandeza, valor_complexo):
            row = self.tabela.rowCount(); self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(agrupamento)); self.tabela.setItem(row, 1, QTableWidgetItem(grandeza))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{abs(valor_complexo):.2f} ∠ {np.angle(valor_complexo, deg=True):.2f}°"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{valor_complexo.real:.2f} + j({valor_complexo.imag:.2f})"))
        
        def add_power_row(agrupamento, grandeza, S):
            row = self.tabela.rowCount(); self.tabela.insertRow(row)
            P, Q = S.real, S.imag
            fp_val = P / abs(S) if abs(S) > 1e-9 else 1.0
            fp_status = "adiantado" if Q < 0 else "atrasado"
            self.tabela.setItem(row, 0, QTableWidgetItem(agrupamento)); self.tabela.setItem(row, 1, QTableWidgetItem(grandeza))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"{abs(S):.2f} VA ∠ {np.angle(S, deg=True):.2f}°"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{P:.2f} + j({Q:.2f})"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"{P:.2f} W"))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"{Q:.2f} VAR"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{abs(fp_val):.3f} {fp_status}"))

        add_separator_row(f"--- Resumo do Motor {nome_motor} ---")
        nos_motor = set(); [nos_motor.update([c['n1'], c['n2']]) for c in comps_motor]
        is_y = len(nos_motor) == 4
        n1, n2, n3 = comps_motor[0]['n1'], comps_motor[1]['n1'], comps_motor[2]['n1']
        V_ab = self.tensoes[n1] - self.tensoes[n2]
        add_data_row(f"Motor {nome_motor}", "Tensão de Linha Média (V_LL)", V_ab)
        if is_y:
            neutro = list(nos_motor - {n1, n2, n3})[0]
            V_an = self.tensoes[n1] - self.tensoes.get(neutro, 0)
            I_a = self.correntes[comps_motor[0]['nome']]
            add_data_row(f"Motor {nome_motor}", "Tensão de Fase Média (V_LN)", V_an)
            add_data_row(f"Motor {nome_motor}", "Corrente de Linha/Fase (I_L)", I_a)
        else: # Delta
            I_ab = self.correntes[comps_motor[0]['nome']]
            I_ca_comp_nome = next(c['nome'] for c in comps_motor if c['n1'] == n3 and c['n2'] == n1)
            I_ca = self.correntes[I_ca_comp_nome]; I_L_a = I_ab - I_ca
            add_data_row(f"Motor {nome_motor}", "Tensão de Fase (V_LL)", V_ab)
            add_data_row(f"Motor {nome_motor}", "Corrente de Fase Média (I_ph)", I_ab)
            add_data_row(f"Motor {nome_motor}", "Corrente de Linha Média (I_L)", I_L_a)
        S_total = sum(self.potencias[c['nome']] for c in comps_motor)
        add_power_row(f"Motor {nome_motor}", "Potência Trifásica Total", S_total)

    # (O restante do código permanece o mesmo)
    def _create_menu_bar(self):
        menu_bar = self.menuBar(); menu_arquivo = menu_bar.addMenu("&Arquivo")
        abrir_action = QAction("&Abrir Netlist...", self); abrir_action.triggered.connect(self.abrir_arquivo); menu_arquivo.addAction(abrir_action)
        salvar_action = QAction("&Salvar Netlist Como...", self); salvar_action.triggered.connect(self.salvar_arquivo_como); menu_arquivo.addAction(salvar_action)
        menu_arquivo.addSeparator(); sair_action = QAction("&Sair", self); sair_action.triggered.connect(self.close); menu_arquivo.addAction(sair_action)
    def abrir_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Abrir Netlist", "", "Netlist Files (*.net *.txt);;All Files (*)")
        if caminho:
            try:
                with open(caminho, 'r', encoding='utf-8') as f: self.text_edit.setPlainText(f.read())
            except Exception as e: QMessageBox.critical(self, "Erro ao Abrir", f"Não foi possível ler o arquivo:\n{e}")
    def salvar_arquivo_como(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Netlist Como", "", "Netlist Files (*.net *.txt);;All Files (*)")
        if caminho:
            try:
                with open(caminho, 'w', encoding='utf-8') as f: f.write(self.text_edit.toPlainText())
            except Exception as e: QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")
    def setup_graficos_tab(self, tab_widget, tipo_grafico):
        main_layout = QHBoxLayout(tab_widget); selection_panel = QVBoxLayout()
        selection_panel.addWidget(QLabel(f"Selecione os Sinais para Plotar ({tipo_grafico.capitalize()})"))
        list_widget = QListWidget(); setattr(self, f"lista_sinais_{tipo_grafico}", list_widget); selection_panel.addWidget(list_widget)
        update_button = QPushButton("📈 Atualizar Gráfico"); update_button.clicked.connect(self.atualizar_graficos); selection_panel.addWidget(update_button)
        main_layout.addLayout(selection_panel); canvas = MplCanvas(); setattr(self, f"{tipo_grafico}_canvas", canvas); main_layout.addWidget(canvas, stretch=1)
    def setup_netlist_tab(self):
        layout = QVBoxLayout(); self.text_edit = QTextEdit(); self.text_edit.setPlaceholderText("Use o formulário abaixo ou digite sua netlist aqui.\nEx: V1 A 0 AC 100 0\n    R1 A B 5k")
        layout.addWidget(self.text_edit); btn_analisar = QPushButton("⚡ Analisar Circuito"); btn_analisar.clicked.connect(self.analisar)
        layout.addWidget(btn_analisar); layout.addWidget(QLabel("Adicionar Motor Trifásico")); form = QFormLayout()
        self.tipo_motor = QComboBox(); self.tipo_motor.addItems(["Estrela (Y)", "Triângulo (Δ)"])
        self.noA = QLineEdit("A"); self.noB = QLineEdit("B"); self.noC = QLineEdit("C"); self.noN = QLineEdit("N"); self.potencia = QLineEdit("3000"); self.fp = QLineEdit("0.9")
        form.addRow("Tipo de Ligação:", self.tipo_motor); form.addRow("Nó A:", self.noA); form.addRow("Nó B:", self.noB); form.addRow("Nó C:", self.noC)
        form.addRow("Nó Neutro (Y apenas):", self.noN); form.addRow("Potência (W):", self.potencia); form.addRow("Fator de Potência:", self.fp)
        layout.addLayout(form); btn_inserir_motor = QPushButton("➕ Inserir Motor na Netlist"); btn_inserir_motor.clicked.connect(self.inserir_motor_netlist)
        layout.addWidget(btn_inserir_motor); self.tab_netlist.setLayout(layout)
    def inserir_motor_netlist(self):
        tipo = self.tipo_motor.currentText(); a = self.noA.text().strip(); b = self.noB.text().strip(); c = self.noC.text().strip()
        n = self.noN.text().strip(); p_str = self.potencia.text().strip(); fp_val_str = self.fp.text().strip()
        nome_motor = f"M{np.random.randint(100,999)}"; potencia_w = float(p_str); fp = float(fp_val_str)
        ligacao = 'Y' if tipo.startswith("Estrela") else 'D'
        z = parser.calcular_impedancia_motor(potencia_w, fp, ligacao=ligacao, tensao_fase=220)
        motor_lines = [];
        if ligacao == 'Y':
            motor_lines.append(f"Z_{nome_motor}_A {a} {n} {z.real} {z.imag}"); motor_lines.append(f"Z_{nome_motor}_B {b} {n} {z.real} {z.imag}"); motor_lines.append(f"Z_{nome_motor}_C {c} {n} {z.real} {z.imag}")
        else:
            motor_lines.append(f"Z_{nome_motor}_AB {a} {b} {z.real} {z.imag}"); motor_lines.append(f"Z_{nome_motor}_BC {b} {c} {z.real} {z.imag}"); motor_lines.append(f"Z_{nome_motor}_CA {c} {a} {z.real} {z.imag}")
        fontes = [f"V_A {a} 0 AC 220 0", f"V_B {b} 0 AC 220 -120", f"V_C {c} 0 AC 220 120"]
        extra = [f"R_N {n} 0 0.001"] if tipo.startswith("Estrela") else []
        texto_atual = self.text_edit.toPlainText().strip().splitlines(); linhas_existentes = set(l.strip().split()[0] for l in texto_atual)
        novas_linhas = [v for v in fontes if v.split()[0] not in linhas_existentes]
        novas_linhas.extend(motor_lines); novas_linhas.extend(extra); self.text_edit.setText("\n".join(texto_atual + novas_linhas))
    def setup_resultados_tab(self):
        layout = QVBoxLayout(); self.tabela = QTableWidget(); layout.addWidget(self.tabela)
        btn_exportar = QPushButton("💾 Exportar para CSV"); btn_exportar.clicked.connect(self.exportar_para_csv)
        hbox = QHBoxLayout(); hbox.addStretch(1); hbox.addWidget(btn_exportar); layout.addLayout(hbox); self.tab_resultados.setLayout(layout)
    def analisar(self):
        texto = self.text_edit.toPlainText()
        if not texto.strip(): QMessageBox.warning(self, "Aviso", "A netlist está vazia."); return
        try:
            self.componentes = parser.parse_netlist_linhas(texto.strip().split('\n'))
            self.tensoes, self.correntes, self.potencias = analise.montar_matriz_anm(self.componentes, self.frequencia)
            self.todos_sinais = []
            self.todos_sinais.extend([{"nome": f"V({n})", "valor": v} for n, v in self.tensoes.items() if n != '0'])
            self.todos_sinais.extend([{"nome": f"I({n})", "valor": i} for n, i in self.correntes.items()])
            self.atualizar_tabela()
            self.popular_listas_de_sinais()
            self.atualizar_graficos()
            self.tabs.setCurrentIndex(1)
        except Exception as e: QMessageBox.critical(self, "Erro na Análise", f"Ocorreu um erro:\n{e}")
    def popular_listas_de_sinais(self):
        self.lista_sinais_fasores.clear(); self.lista_sinais_ondas.clear()
        for sinal in self.todos_sinais:
            nome_sinal = sinal["nome"]
            item_fasor = QListWidgetItem(nome_sinal); item_fasor.setFlags(item_fasor.flags() | Qt.ItemFlag.ItemIsUserCheckable); item_fasor.setCheckState(Qt.CheckState.Checked); self.lista_sinais_fasores.addItem(item_fasor)
            item_onda = QListWidgetItem(nome_sinal); item_onda.setFlags(item_onda.flags() | Qt.ItemFlag.ItemIsUserCheckable); item_onda.setCheckState(Qt.CheckState.Checked); self.lista_sinais_ondas.addItem(item_onda)
    def atualizar_graficos(self):
        def get_selected_data(list_widget):
            dados_selecionados = []; nomes_selecionados = [list_widget.item(i).text() for i in range(list_widget.count()) if list_widget.item(i).checkState() == Qt.CheckState.Checked]
            for sinal in self.todos_sinais:
                if sinal["nome"] in nomes_selecionados: dados_selecionados.append(sinal)
            return dados_selecionados
        dados_fasores = get_selected_data(self.lista_sinais_fasores);
        if dados_fasores: fasores.plotar_fasores(self.fasores_canvas.ax, dados_fasores)
        else: self.fasores_canvas.clear()
        self.fasores_canvas.draw()
        dados_ondas = get_selected_data(self.lista_sinais_ondas)
        if dados_ondas: ondas.plotar_ondas(self.ondas_canvas.ax, dados_ondas, f=self.frequencia)
        else: self.ondas_canvas.clear()
        self.ondas_canvas.draw()
    def exportar_para_csv(self):
        if self.tabela.rowCount() == 0: QMessageBox.warning(self, "Aviso", "Não há dados na tabela para exportar."); return
        caminho_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Resultados", "", "CSV Files (*.csv);;All Files (*)")
        if not caminho_arquivo: return
        try:
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                writer = csv.writer(arquivo_csv, delimiter=';'); headers = [self.tabela.horizontalHeaderItem(i).text() for i in range(self.tabela.columnCount())]
                writer.writerow(headers)
                for row in range(self.tabela.rowCount()):
                    linha_dados = []; is_separator = self.tabela.columnSpan(row, 0) > 1
                    if is_separator:
                        item = self.tabela.item(row, 0); linha_dados.append(item.text() if item else '')
                    else:
                        for col in range(self.tabela.columnCount()):
                            item = self.tabela.item(row, col); linha_dados.append(item.text() if item else '')
                    writer.writerow(linha_dados)
            QMessageBox.information(self, "Sucesso", f"Resultados exportados para:\n{caminho_arquivo}")
        except Exception as e: QMessageBox.critical(self, "Erro de Exportação", f"Não foi possível salvar o arquivo:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())