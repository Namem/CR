# schematic/dependent_source_item.py

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF

class DependentSourceItem(QGraphicsPathItem):
    def __init__(self, name, value_str, source_type='V'):
        super().__init__()
        self.name = name
        self.value_str = value_str

        # Desenha o losango (diamante)
        path = QPainterPath()
        path.moveTo(0, -20); path.lineTo(15, 0)
        path.lineTo(0, 20); path.lineTo(-15, 0)
        path.closeSubpath()

        # Adiciona os sinais de + e - para fontes de tensão
        if source_type in ['E', 'H']: # Fontes de Tensão
            path.moveTo(-8, -10); path.lineTo(-2, -10) # Sinal de +
            path.moveTo(-5, -13); path.lineTo(-5, -7)
            path.moveTo(-8, 10); path.lineTo(-2, 10)  # Sinal de -
        
        # Adiciona uma seta para fontes de corrente
        elif source_type in ['F', 'G']: # Fontes de Corrente
            path.moveTo(0, -12); path.lineTo(0, 12)
            path.moveTo(-5, 7); path.lineTo(0, 12); path.lineTo(5, 7)

        # Linhas de conexão
        path.moveTo(0, -20); path.lineTo(0, -25)
        path.moveTo(0, 20); path.lineTo(0, 25)

        self.setPath(path)
        
        pen = QPen(QColor(255, 165, 0), 2) # Laranja
        self.setPen(pen)

    def get_terminals(self):
        # Pontos de conexão exatos nas extremidades
        return QPointF(0, -25), QPointF(0, 25)