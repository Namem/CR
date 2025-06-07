# interface/schematic_scene.py

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtCore import Qt

class SchematicScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid_size = 20
        self.setBackgroundBrush(QColor(30, 30, 30)) # Fundo escuro

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Define a cor e o estilo da caneta para a grade
        pen = QPen(QColor(60, 60, 60))
        pen.setWidth(0)
        painter.setPen(pen)

        # Desenha os pontos da grade
        left = int(rect.left()) - int(rect.left()) % self.grid_size
        top = int(rect.top()) - int(rect.top()) % self.grid_size

        points = []
        for x in range(left, int(rect.right()), self.grid_size):
            for y in range(top, int(rect.bottom()), self.grid_size):
                points.append((x, y))
        
        for p in points:
            painter.drawPoint(p[0], p[1])