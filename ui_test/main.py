from PyQt6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, Theme, setTheme
from ui import Demo

app = QApplication([])

# Apply dark theme
# setTheme(Theme.DARK)

demo = Demo()
demo.show()
app.exec()
