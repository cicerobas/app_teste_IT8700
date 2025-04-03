from PySide6.QtCore import QSize, QRect
from PySide6.QtWidgets import QLayout


class FlowLayout(QLayout):
    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self._items = []
        self.setSpacing(spacing)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        return self._items[index] if 0 <= index < len(self._items) else None

    def takeAt(self, index):
        return self._items.pop(index) if 0 <= index < len(self._items) else None

    def setGeometry(self, rect):
        super().setGeometry(rect)
        x, y, row_height = rect.x(), rect.y(), 0
        for item in self._items:
            widget = item.widget()
            if widget is not None:
                size = widget.size()
                if x + size.width() > rect.right():
                    x = rect.x()
                    y += row_height + self.spacing()
                    row_height = 0
                item.setGeometry(QRect(x, y, size.width(), size.height()))
                x += size.width() + self.spacing()
                row_height = max(row_height, size.height())

    def sizeHint(self):
        return QSize(400, 300)

    def minimumSize(self):
        return QSize(100, 100)
