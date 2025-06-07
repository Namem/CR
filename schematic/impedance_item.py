# schematic/impedance_item.py

from PySide6.QtWidgets import QGraphicsPathItem
from PySide6.QtGui import QPen, QColor, QPainterPath

class ImpedanceItem(QGraphicsPathItem):
    def __init__(self, name, value_str):
        super().__init__()
        self.name = name
        self.value_str = value_str
        
        path = QPainterPath()
        path.moveTo(-30, 0)
        path.lineTo(-15, 0)
        path.addRect(-15, -10, 30, 20)
        path.moveTo(15, 0)
        path.lineTo(30, 0)

        self.setPath(path)
        
        pen = QPen(QColor(200, 200, 200), 2) # Cinza claro
        self.setPen(pen)

    def get_terminals(self):
        return QPainterPath(self.path().elementAt(0)).pointAtPercent(0), \
               QPainterPath(self.path().elementAt(2)).pointAtPercent(1)