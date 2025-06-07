# schematic/node_item.py

from PySide6.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt

class NodeItem(QGraphicsEllipseItem):
    def __init__(self, name, x, y, radius=10):
        # O retângulo que define a elipse
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setPos(x, y) # Define a posição do item na cena

        # Propriedades visuais do círculo
        self.setBrush(QBrush(QColor("red")))
        self.setPen(QPen(Qt.PenStyle.NoPen))
        self.setZValue(1) # Garante que o nó fique na frente dos fios

        # Texto com o nome do nó
        self.label = QGraphicsTextItem(name, self)
        self.label.setDefaultTextColor(QColor("white"))
        
        # Centraliza o texto
        label_rect = self.label.boundingRect()
        self.label.setPos(-label_rect.width() / 2, -label_rect.height() / 2)