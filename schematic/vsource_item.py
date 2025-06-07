# schematic/vsource_item.py

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath
from PySide6.QtCore import QPointF

class VSourceItem(QGraphicsPathItem):
    def __init__(self, name, value_str):
        super().__init__()
        self.name = name
        self.value_str = value_str

        path = QPainterPath()
        path.addEllipse(-15, -15, 30, 30); path.moveTo(-25, 0)
        path.lineTo(-15, 0); path.moveTo(15, 0); path.lineTo(25, 0)
        path.moveTo(-10, 0); path.quadTo(-5, -10, 0, 0); path.quadTo(5, 10, 10, 0)
        self.setPath(path)
        
        pen = QPen(QColor("magenta"), 2)
        self.setPen(pen)
        
    def get_terminals(self):
        # Pontos de conexão exatos nas extremidades
        return QPointF(-25, 0), QPointF(25, 0)