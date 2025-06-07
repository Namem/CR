# main.py

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit,
    QPushButton, QLabel, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QHeaderView, QFileDialog,
    QListWidget, QListWidgetItem, QGraphicsView, QGraphicsLineItem
)
from PySide6.QtGui import QAction, QColor, QTextCursor, QTextCharFormat, QPainter, QPen
from PySide6.QtCore import Qt, QPointF
import sys
import numpy as np
import csv
from collections import defaultdict, deque

# Importe os módulos do projeto
from netlist_parser import parser
from core import analise
from interface.canvas import MplCanvas
from graphics import fasores, ondas
from interface.schematic_scene import SchematicScene
from schematic.node_item import NodeItem
from schematic.resistor_item import ResistorItem
from schematic.vsource_item import VSourceItem
from schematic.inductor_item import InductorItem
from schematic.capacitor_item import CapacitorItem
from schematic.impedance_item import ImpedanceItem
from schematic.dependent_source_item import DependentSourceItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choque de Realidade - Analisador CA")
        self.setGeometry(100, 100, 1200, 800)

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
        self.tab_esquematico = QWidget()
        self.tab_fasores = QWidget()
        self.tab_ondas = QWidget()

        self.tabs.addTab(self.tab_netlist, "📝 Netlist")
        self.tabs.addTab(self.tab_resultados, "⚡ Resultados")
        self.tabs.addTab(self.tab_esquematico, "✍️ Esquemático")
        self.tabs.addTab(self.tab_fasores, "📊 Fasores")
        self.tabs.addTab(self.tab_ondas, "🌊 Ondas")

        self.setup_netlist_tab()
        self.setup_resultados_tab()
        self.setup_esquematico_tab()
        self.setup_graficos_tab(self.tab_fasores, "fasores")
        self.setup_graficos_tab(self.tab_ondas, "ondas")

    def _create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Menu Arquivo
        menu_arquivo = menu_bar.addMenu("&Arquivo")
        abrir_action = QAction("&Abrir Netlist...", self)
        abrir_action.triggered.connect(self.abrir_arquivo)
        menu_arquivo.addAction(abrir_action)
        
        salvar_action = QAction("&Salvar Netlist Como...", self)
        salvar_action.triggered.connect(self.salvar_arquivo_como)
        menu_arquivo.addAction(salvar_action)
        
        menu_arquivo.addSeparator()
        
        sair_action = QAction("&Sair", self)
        sair_action.triggered.connect(self.close)
        menu_arquivo.addAction(sair_action)

        # Novo Menu Visualizar
        menu_view = menu_bar.addMenu("&Visualizar")
        
        tema_dracula_action = QAction("Tema Escuro (Dracula)", self)
        tema_dracula_action.triggered.connect(lambda: self.carregar_estilo("interface/style.qss"))
        menu_view.addAction(tema_dracula_action)
        
        tema_claro_action = QAction("Tema Claro", self)
        tema_claro_action.triggered.connect(lambda: self.carregar_estilo("interface/light_style.qss"))
        menu_view.addAction(tema_claro_action)

        tema_ocean_action = QAction("Tema Oceano", self)
        tema_ocean_action.triggered.connect(lambda: self.carregar_estilo("interface/ocean_style.qss"))
        menu_view.addAction(tema_ocean_action)

        # Menu Ajuda
        menu_ajuda = menu_bar.addMenu("&Ajuda")
        sobre_action = QAction("&Sobre o Choque de Realidade", self)
        sobre_action.triggered.connect(self.mostrar_janela_ajuda)
        menu_ajuda.addAction(sobre_action)

    def carregar_estilo(self, caminho_arquivo):
        """Carrega e aplica um arquivo de folha de estilos (QSS) à aplicação."""
        try:
            with open(caminho_arquivo, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Arquivo de estilo não encontrado: {caminho_arquivo}. Usando estilo padrão.")
            self.setStyleSheet("") # Reseta para o estilo padrão do sistema

    def mostrar_janela_ajuda(self):
        titulo = "Sobre o Choque de Realidade - Analisador CA"
        texto = """
        <p><b>Choque de Realidade</b> é um analisador de circuitos de corrente alternada (CA) 
        desenvolvido para fins educacionais e técnicos.</p>
        <h3>Funcionalidades Principais:</h3>
        <ul>
            <li><b>Análise Nodal Modificada (ANM):</b> Capaz de resolver qualquer topologia de circuito.</li>
            <li><b>Suporte a Componentes:</b> R, L, C, Z, fontes de tensão independentes e 
            fontes dependentes (VCVS, VCCS, CCCS, CCVS).</li>
            <li><b>Resultados Completos:</b> Calcula tensões, correntes e potências complexas (P, Q, S, FP).</li>
            <li><b>Visualização Gráfica:</b> Gera automaticamente um esquemático do circuito, 
            diagrama de fasores e formas de onda.</li>
            <li><b>Recursos de Usabilidade:</b> Suporte a unidades (k, m, u), Abrir/Salvar netlists, 
            Exportar resultados para CSV e destaque de erros na netlist.</li>
        </ul>
        <h3>Como Usar:</h3>
        <ol>
            <li><b>Escreva a Netlist:</b> Digite ou cole o seu circuito na aba "Netlist" 
            usando o formato SPICE (ex: <code>R1 A B 1k</code>).</li>
            <li><b>Analise:</b> Clique no botão "Analisar Circuito".</li>
            <li><b>Explore:</b> Navegue pelas abas "Resultados", "Esquemático", "Fasores" e "Ondas" 
            para visualizar a análise completa.</li>
        </ol>
        <p><i>Desenvolvido com a assistência da IA do Google.</i></p>
        """
        QMessageBox.about(self, titulo, texto)

    def abrir_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Abrir Netlist", "", "Netlist Files (*.net *.txt);;All Files (*)")
        if caminho:
            try:
                with open(caminho, 'r', encoding='utf-8') as f:
                    self.text_edit.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Abrir", f"Não foi possível ler o arquivo:\n{e}")

    def salvar_arquivo_como(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Netlist Como", "", "Netlist Files (*.net *.txt);;All Files (*)")
        if caminho:
            try:
                with open(caminho, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    def setup_graficos_tab(self, tab_widget, tipo_grafico):
        main_layout = QHBoxLayout(tab_widget)
        selection_panel = QVBoxLayout()
        selection_panel.addWidget(QLabel(f"Selecione os Sinais para Plotar ({tipo_grafico.capitalize()})"))
        list_widget = QListWidget()
        setattr(self, f"lista_sinais_{tipo_grafico}", list_widget)
        selection_panel.addWidget(list_widget)
        update_button = QPushButton("📈 Atualizar Gráfico")
        update_button.clicked.connect(self.atualizar_graficos)
        selection_panel.addWidget(update_button)
        main_layout.addLayout(selection_panel)
        canvas = MplCanvas()
        setattr(self, f"{tipo_grafico}_canvas", canvas)
        main_layout.addWidget(canvas, stretch=1)

    def setup_esquematico_tab(self):
        layout = QVBoxLayout(self.tab_esquematico)
        self.scene = SchematicScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        layout.addWidget(self.view)

    def setup_netlist_tab(self):
        layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Use o formulário abaixo ou digite sua netlist aqui.\nEx: V1 A 0 AC 100 0\n    R1 A B 5k")
        layout.addWidget(self.text_edit)
        btn_analisar = QPushButton("⚡ Analisar Circuito")
        btn_analisar.clicked.connect(self.analisar)
        layout.addWidget(btn_analisar)
        layout.addWidget(QLabel("Adicionar Motor Trifásico"))
        form = QFormLayout()
        self.tipo_motor = QComboBox()
        self.tipo_motor.addItems(["Estrela (Y)", "Triângulo (Δ)"])
        self.noA = QLineEdit("A"); self.noB = QLineEdit("B"); self.noC = QLineEdit("C")
        self.noN = QLineEdit("N"); self.potencia = QLineEdit("3000"); self.fp = QLineEdit("0.9")
        form.addRow("Tipo de Ligação:", self.tipo_motor)
        form.addRow("Nó A:", self.noA); form.addRow("Nó B:", self.noB); form.addRow("Nó C:", self.noC)
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
        a = self.noA.text().strip(); b = self.noB.text().strip(); c = self.noC.text().strip()
        n = self.noN.text().strip(); p_str = self.potencia.text().strip(); fp_val_str = self.fp.text().strip()
        nome_motor = f"M{np.random.randint(100,999)}"
        potencia_w = float(p_str); fp = float(fp_val_str)
        ligacao = 'Y' if tipo.startswith("Estrela") else 'D'
        z = parser.calcular_impedancia_motor(potencia_w, fp, ligacao=ligacao, tensao_fase=220)
        motor_lines = []
        if ligacao == 'Y':
            motor_lines.append(f"Z_{nome_motor}_A {a} {n} {z.real} {z.imag}")
            motor_lines.append(f"Z_{nome_motor}_B {b} {n} {z.real} {z.imag}")
            motor_lines.append(f"Z_{nome_motor}_C {c} {n} {z.real} {z.imag}")
        else: # Delta
            motor_lines.append(f"Z_{nome_motor}_AB {a} {b} {z.real} {z.imag}")
            motor_lines.append(f"Z_{nome_motor}_BC {b} {c} {z.real} {z.imag}")
            motor_lines.append(f"Z_{nome_motor}_CA {c} {a} {z.real} {z.imag}")
        fontes = [f"V_A {a} 0 AC 220 0", f"V_B {b} 0 AC 220 -120", f"V_C {c} 0 AC 220 120"]
        extra = [f"R_N {n} 0 0.001"] if tipo.startswith("Estrela") else []
        texto_atual = self.text_edit.toPlainText().strip().splitlines()
        linhas_existentes = set(l.strip().split()[0] for l in texto_atual)
        novas_linhas = [v for v in fontes if v.split()[0] not in linhas_existentes]
        novas_linhas.extend(motor_lines)
        novas_linhas.extend(extra)
        self.text_edit.setText("\n".join(texto_atual + novas_linhas))

    def setup_resultados_tab(self):
        layout = QVBoxLayout()
        self.tabela = QTableWidget()
        layout.addWidget(self.tabela)
        btn_exportar = QPushButton("💾 Exportar para CSV")
        btn_exportar.clicked.connect(self.exportar_para_csv)
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(btn_exportar)
        layout.addLayout(hbox)
        self.tab_resultados.setLayout(layout)

    def analisar(self):
        self.limpar_destaque()
        texto = self.text_edit.toPlainText()
        if not texto.strip():
            QMessageBox.warning(self, "Aviso", "A netlist está vazia.")
            return
        try:
            self.componentes = parser.parse_netlist_linhas(texto.strip().split('\n'))
            self.tensoes, self.correntes, self.potencias = analise.montar_matriz_anm(self.componentes, self.frequencia)
            self.todos_sinais = []
            self.todos_sinais.extend([{"nome": f"V({n})", "valor": v} for n, v in self.tensoes.items() if n != '0'])
            self.todos_sinais.extend([{"nome": f"I({n})", "valor": i} for n, i in self.correntes.items()])
            self.atualizar_tabela()
            self.desenhar_esquematico()
            self.popular_listas_de_sinais()
            self.atualizar_graficos()
            self.tabs.setCurrentIndex(1)
        except parser.NetlistParseError as e:
            QMessageBox.critical(self, "Erro na Netlist", str(e))
            self.destacar_linha_erro(e.line_number)
        except Exception as e:
            QMessageBox.critical(self, "Erro na Análise", f"Ocorreu um erro inesperado:\n{e}")

    def popular_listas_de_sinais(self):
        self.lista_sinais_fasores.clear()
        self.lista_sinais_ondas.clear()
        for sinal in self.todos_sinais:
            nome_sinal = sinal["nome"]
            item_fasor = QListWidgetItem(nome_sinal)
            item_fasor.setFlags(item_fasor.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item_fasor.setCheckState(Qt.CheckState.Checked)
            self.lista_sinais_fasores.addItem(item_fasor)
            item_onda = QListWidgetItem(nome_sinal)
            item_onda.setFlags(item_onda.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item_onda.setCheckState(Qt.CheckState.Checked)
            self.lista_sinais_ondas.addItem(item_onda)

    def atualizar_graficos(self):
        def get_selected_data(list_widget):
            dados_selecionados = []
            nomes_selecionados = [list_widget.item(i).text() for i in range(list_widget.count()) if list_widget.item(i).checkState() == Qt.CheckState.Checked]
            for sinal in self.todos_sinais:
                if sinal["nome"] in nomes_selecionados:
                    dados_selecionados.append(sinal)
            return dados_selecionados
        
        dados_fasores = get_selected_data(self.lista_sinais_fasores)
        if dados_fasores:
            fasores.plotar_fasores(self.fasores_canvas.ax, dados_fasores)
        else:
            self.fasores_canvas.clear()
        self.fasores_canvas.draw()
        
        dados_ondas = get_selected_data(self.lista_sinais_ondas)
        if dados_ondas:
            ondas.plotar_ondas(self.ondas_canvas.ax, dados_ondas, f=self.frequencia)
        else:
            self.ondas_canvas.clear()
        self.ondas_canvas.draw()

    def desenhar_esquematico(self):
        self.scene.clear()
        all_nodes = list(self.tensoes.keys())
        if not all_nodes: return

        adj = defaultdict(list)
        for comp in self.componentes:
            adj[comp['n1']].append(comp['n2'])
            adj[comp['n2']].append(comp['n1'])

        levels = {node: -1 for node in all_nodes}
        max_level = 0
        if '0' in all_nodes:
            queue = deque([('0', 0)])
            visited = {'0'}
            levels['0'] = 0
            
            while queue:
                curr_node, level = queue.popleft()
                max_level = max(max_level, level)
                for neighbor in adj[curr_node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        levels[neighbor] = level + 1
                        queue.append((neighbor, level + 1))
        
        level_unconnected = max_level + 1
        for node in all_nodes:
            if levels[node] == -1:
                levels[node] = level_unconnected
                level_unconnected += 1
        
        nodes_by_level = defaultdict(list)
        for node, level in levels.items():
            nodes_by_level[level].append(node)

        node_positions = {}
        y_step, x_step = 150, 200
        for level, nodes_in_level in sorted(nodes_by_level.items()):
            y = -level * y_step
            width = (len(nodes_in_level) - 1) * x_step
            start_x = -width / 2
            for i, node_name in enumerate(sorted(nodes_in_level)):
                x = start_x + i * x_step
                node_positions[node_name] = QPointF(x, y)
                self.scene.addItem(NodeItem(node_name, x, y))

        parallel_groups = defaultdict(list)
        for comp in self.componentes:
            key = tuple(sorted((comp['n1'], comp['n2'])))
            parallel_groups[key].append(comp)
        
        wire_pen = QPen(QColor(160, 160, 160), 1)
        
        for node_pair, comps in parallel_groups.items():
            n1, n2 = node_pair
            if n1 not in node_positions or n2 not in node_positions: continue
                
            pos1, pos2 = node_positions[n1], node_positions[n2]
            line_vec = pos2 - pos1
            perp_vec = QPointF(-line_vec.y(), line_vec.x())
            norm_perp_vec = perp_vec / np.sqrt(perp_vec.x()**2 + perp_vec.y()**2) if (perp_vec.x()**2 + perp_vec.y()**2) > 0 else QPointF(0,0)

            for i, comp in enumerate(comps):
                offset_dist = 40
                shift = (i - (len(comps) - 1) / 2.0) * offset_dist
                offset = norm_perp_vec * shift
                mid_point = ((pos1 + pos2) / 2) + offset
                
                comp_item = self.criar_item_componente(comp)
                if comp_item:
                    angle_rad = np.arctan2(line_vec.y(), line_vec.x())
                    angle_deg = np.rad2deg(angle_rad)
                    comp_item.setPos(mid_point)
                    comp_item.setRotation(angle_deg)
                    self.scene.addItem(comp_item)
                    
                    term1, term2 = comp_item.get_terminals()
                    scene_term1, scene_term2 = comp_item.mapToScene(term1), comp_item.mapToScene(term2)
                    
                    wire1 = QGraphicsLineItem(pos1.x(), pos1.y(), scene_term1.x(), scene_term1.y())
                    wire1.setPen(wire_pen)
                    self.scene.addItem(wire1)
                    
                    wire2 = QGraphicsLineItem(pos2.x(), pos2.y(), scene_term2.x(), scene_term2.y())
                    wire2.setPen(wire_pen)
                    self.scene.addItem(wire2)

        self.view.fitInView(self.scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def criar_item_componente(self, comp):
        tipo = comp['tipo']
        valor = comp['valor']

        if tipo == 'V': return VSourceItem(comp['nome'], f"{valor}V")
        elif tipo == 'R': return ResistorItem(comp['nome'], f"{valor}Ω")
        elif tipo == 'L': return InductorItem(comp['nome'], f"{valor}H")
        elif tipo == 'C': return CapacitorItem(comp['nome'], f"{valor}F")
        elif tipo == 'Z': return ImpedanceItem(comp['nome'], f"{valor}Ω")
        elif tipo in ['E', 'G', 'F', 'H']:
            return DependentSourceItem(comp['nome'], f"{valor}", source_type=tipo)
        return None

    def atualizar_tabela(self):
        self.tabela.clear()
        self.tabela.setRowCount(0)
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "Agrupamento", "Grandeza", "Valor Polar", "Valor Retangular", 
            "Potência Ativa (P)", "Potência Reativa (Q)", "Fator de Potência (FP)"
        ])
        
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

        add_separator_row("--- Tensões Nodais ---")
        for nome, valor in sorted(self.tensoes.items()):
            if nome == '0': continue
            add_data_row(f"Nó '{nome}'", f"Tensão V({nome})", valor)

        for comp in self.componentes:
            nome = comp['nome']
            add_separator_row(f"--- Componente: {nome} ---")
            if not nome.startswith('Vctrl_'):
                add_data_row(nome, f"Corrente I({nome})", self.correntes[nome])
            add_power_row(nome, f"Potência S({nome})", self.potencias[nome])

        motores_agrupados = defaultdict(list)
        for comp in self.componentes:
            if comp['nome'].startswith('Z_M'):
                partes = comp['nome'].split('_')
                nome_motor = partes[1]
                if nome_motor not in motores_agrupados:
                    motores_agrupados[nome_motor] = []
                motores_agrupados[nome_motor].append(comp)
        
        for nome_motor, comps_motor in motores_agrupados.items():
            if len(comps_motor) == 3:
                self.adicionar_resumo_trifasico_agrupado(nome_motor, comps_motor)

        self.tabela.resizeColumnsToContents()

    def adicionar_resumo_trifasico_agrupado(self, nome_motor, comps_motor):
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
        
        add_separator_row(f"--- Resumo do Motor {nome_motor} ---")
        nos_motor = set()
        for c in comps_motor:
            nos_motor.add(c['n1'])
            nos_motor.add(c['n2'])
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
            I_ca = self.correntes[I_ca_comp_nome]
            I_L_a = I_ab - I_ca
            add_data_row(f"Motor {nome_motor}", "Tensão de Fase (V_LL)", V_ab)
            add_data_row(f"Motor {nome_motor}", "Corrente de Fase Média (I_ph)", I_ab)
            add_data_row(f"Motor {nome_motor}", "Corrente de Linha Média (I_L)", I_L_a)
        
        S_total = sum(self.potencias[c['nome']] for c in comps_motor)
        add_power_row(f"Motor {nome_motor}", "Potência Trifásica Total", S_total)

    def exportar_para_csv(self):
        if self.tabela.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Não há dados na tabela para exportar.")
            return
        caminho_arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Resultados", "", "CSV Files (*.csv);;All Files (*)")
        if not caminho_arquivo:
            return
        try:
            with open(caminho_arquivo, 'w', newline='', encoding='utf-8') as arquivo_csv:
                writer = csv.writer(arquivo_csv, delimiter=';')
                headers = [self.tabela.horizontalHeaderItem(i).text() for i in range(self.tabela.columnCount())]
                writer.writerow(headers)
                for row in range(self.tabela.rowCount()):
                    linha_dados = []
                    is_separator = self.tabela.columnSpan(row, 0) > 1
                    if is_separator:
                        item = self.tabela.item(row, 0)
                        linha_dados.append(item.text() if item else '')
                    else:
                        for col in range(self.tabela.columnCount()):
                            item = self.tabela.item(row, col)
                            linha_dados.append(item.text() if item else '')
                    writer.writerow(linha_dados)
            QMessageBox.information(self, "Sucesso", f"Resultados exportados para:\n{caminho_arquivo}")
        except Exception as e:
            QMessageBox.critical(self, "Erro de Exportação", f"Não foi possível salvar o arquivo:\n{e}")

    def limpar_destaque(self):
        fmt = QTextCharFormat()
        fmt.clearBackground()
        cursor = self.text_edit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(fmt)
        cursor.clearSelection()
        self.text_edit.setTextCursor(cursor)

    def destacar_linha_erro(self, linha_numero):
        fmt = QTextCharFormat()
        fmt.setBackground(QColor(139, 0, 0, 150))
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, linha_numero - 1)
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.setCharFormat(fmt)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Carrega o estilo ao iniciar a aplicação
    try:
        with open("interface/style.qss", "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Arquivo de estilo (interface/style.qss) não encontrado. Usando estilo padrão.")
        
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())
#finalizado