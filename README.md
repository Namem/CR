# ⚡ Choque de Realidade – Analisador de Circuitos CA

**Choque de Realidade** é uma aplicação desktop desenvolvida em Python para análise de circuitos elétricos em corrente alternada (CA), com entrada via netlist e interface gráfica interativa. O foco principal está na análise monofásica com visualização de resultados de forma clara e objetiva.

## 🧩 Funcionalidades Atuais

- Parser de netlist para circuitos CA monofásicos
- Análise nodal automática com suporte a componentes R, L, C e fontes senoidais
- Interface gráfica intuitiva desenvolvida com PySide6
- Visualização de resultados em tabelas e gráficos (formas de onda)
- Renderização gráfica básica dos circuitos

## 🚀 Tecnologias Utilizadas

- **Python 3.11+**
- **PySide6** – Interface gráfica baseada em Qt
- **NumPy** – Manipulação de números complexos
- **Matplotlib** – Geração de gráficos

## 🛠️ Instalação e Execução

Clone o repositório e instale as dependências:

```bash
git clone https://github.com/Namem/CR.git
cd CR
pip install -r requirements.txt
python main.py
```

## 📘 Exemplo de Netlist

```txt
V1 n1 0 senoidal(220 60)
R1 n1 n2 100
L1 n2 0 0.2
```

## 👨‍💻 Autor

**Namem Rachid Jaudy**  
Engenharia da Computação – IFMT  
[GitHub](https://github.com/Namem) • [LinkedIn](https://www.linkedin.com/in/namem-rachid-jaudy-616138124/)

---

> Este projeto está em desenvolvimento contínuo. Contribuições são bem-vindas!
