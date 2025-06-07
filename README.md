Choque de Realidade - Analisador de Circuitos CA
Choque de Realidade é uma aplicação desktop de código aberto, desenvolvida em Python, para análise e simulação de circuitos elétricos em Corrente Alternada (CA). O software foi criado como uma ferramenta educacional e técnica, capaz de resolver circuitos complexos e apresentar os resultados de forma visual e intuitiva.

🎯 Funcionalidades
O software possui um conjunto robusto de funcionalidades para análise de circuitos:

Análise de Circuitos Avançada: Utiliza a Análise Nodal Modificada (ANM) para resolver qualquer topologia de circuito, incluindo fontes flutuantes e em série.
Suporte a Componentes:
Componentes Passivos: Resistor (R), Indutor (L), Capacitor (C) e Impedância (Z).
Fontes Independentes: Fonte de Tensão AC (V).
Fontes Dependentes: Suporte completo para VCVS (E), VCCS (G), CCCS (F), e CCVS (H).
Resultados Detalhados:
Cálculo de tensões nodais complexas.
Cálculo de correntes complexas em todos os componentes.
Cálculo de potências complexas (Aparente S, Ativa P, Reativa Q) e Fator de Potência (FP) para cada componente.
Visualização Completa:
Tabela de Resultados: Apresenta todos os valores calculados de forma organizada e agrupada por componente.
Esquemático Automático: Desenha um diagrama esquemático do circuito a partir da netlist, com um algoritmo de layout hierárquico.
Diagrama Fasorial: Plota os fasores de tensão e corrente para análise vetorial.
Formas de Onda: Exibe os gráficos de amplitude vs. tempo para os sinais de tensão e corrente.
Recursos de Usabilidade:
Editor de Netlist: Com destaque de erro para fácil depuração.
Manipulação de Arquivos: Funcionalidades para Abrir e Salvar arquivos de netlist (.net, .txt).
Exportação: Exporta a tabela de resultados completa para o formato CSV.
Suporte a Unidades: Aceita prefixos padrão do SI na netlist (p, n, u, m, k, meg, g).
Gráficos Interativos: Permite ao usuário selecionar quais sinais exibir nos gráficos.
Assistente Trifásico: Um formulário para gerar automaticamente a netlist de um motor trifásico (Y ou Δ).
🧰 Tecnologias Utilizadas
Linguagem: Python
Interface Gráfica (GUI): PySide6
Cálculos Numéricos: NumPy
Gráficos e Plotagem: Matplotlib
🚀 Como Usar
Escreva a Netlist: Na aba "📝 Netlist", digite a descrição do seu circuito ou abra um arquivo (Arquivo -> Abrir...).
Analise: Clique no botão "⚡ Analisar Circuito". Se houver um erro na sua netlist, a linha correspondente será destacada em vermelho.
Explore os Resultados: Navegue pelas abas para visualizar a análise completa:
"⚡ Resultados": Tabela com todos os valores numéricos.
"✍️ Esquemático": Diagrama visual do seu circuito.
"📊 Fasores": Fasores de tensão e corrente.
"🌊 Ondas": Formas de onda senoidais no domínio do tempo.
✍️ Sintaxe da Netlist
Os componentes são definidos linha por linha, no seguinte formato:

Componente	Sintaxe	Exemplo
Resistor	R<nome> <nó1> <nó2> <valor>	R1 A B 10k
Indutor	L<nome> <nó1> <nó2> <valor>	L1 B 0 10m
Capacitor	C<nome> <nó1> <nó2> <valor>	C1 A B 100u
Impedância	Z<nome> <nó1> <nó2> <real> <imag>	Z1 A B 50 25.5
Fonte de Tensão AC	V<nome> <nó+> <nó-> AC <mag> <fase>	V1 IN 0 AC 10 0
VCVS (E)	E<nome> <nó+> <nó-> <nó_ctrl+> <nó_ctrl-> <ganho>	E_amp OUT 0 IN 0 100k
VCCS (G)	G<nome> <nó+> <nó-> <nó_ctrl+> <nó_ctrl-> <ganho>	G1 A B C D 0.5
CCCS (F)	F<nome> <nó+> <nó-> <nó_ctrl+> <nó_ctrl-> <ganho>	F1 A B C D 50
CCVS (H)	H<nome> <nó+> <nó-> <nó_ctrl+> <nó_ctrl-> <ganho>	H1 A B C D 10

Exportar para as Planilhas
Para fontes F e H, o parser cria uma fonte de tensão de 0V entre <nó_ctrl+> e <nó_ctrl-> para medir a corrente de controle.

⚙️ Instalação e Execução (a partir do código-fonte)
Clone ou baixe os arquivos do projeto.
Crie e ative um ambiente virtual:
Bash

python3 -m venv .venv
source .venv/bin/activate  # No Linux/macOS
# .venv\Scripts\activate   # No Windows
Instale as dependências:
Bash

pip install -r requirements.txt
Execute a aplicação:
Bash

python main.py
📂 Estrutura do Projeto
choque_de_realidade/
├── core/
│   └── analise.py         # Núcleo de análise (ANM)
├── graphics/
│   ├── fasores.py         # Lógica de plotagem de fasores
│   └── ondas.py           # Lógica de plotagem de formas de onda
├── interface/
│   ├── canvas.py          # Widget base do Matplotlib para PySide6
│   └── schematic_scene.py # Cena do esquemático com grade
├── netlist_parser/
│   └── parser.py          # Leitura e interpretação da netlist
├── schematic/
│   ├── ...                # Arquivos de desenho para cada componente visual
├── main.py                # Arquivo principal da aplicação
└── requirements.txt       # Lista de dependências do Python