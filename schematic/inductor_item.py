# schematic/inductor_item.py

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF

class InductorItem(QGraphicsPathItem):
    def __init__(self, name, value_str):
        super().__init__()
        self.name = name
        self.value_str = value_str
        
        path = QPainterPath()
        path.moveTo(-30, 0); path.lineTo(-20, 0)
        path.arcTo(-20, -5, 10, 10, 180, -180); path.arcTo(-10, -5, 10, 10, 180, -180)
        path.arcTo(0, -5, 10, 10, 180, -180); path.arcTo(10, -5, 10, 10, 180, -180)
        path.lineTo(30, 0)
        self.setPath(path)
        
        pen = QPen(QColor("yellow"), 2)
        self.setPen(pen)

    def get_terminals(self):
        # Pontos de conexão exatos nas extremidades
        return QPointF(-30, 0), QPointF(30, 0)