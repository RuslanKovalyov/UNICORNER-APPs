import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setWindowIcon(QIcon('GUI.bird.png'))
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # Add buttons/widgets here
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InventoryApp()
    mainWin.show()
    sys.exit(app.exec_())

# make apk file
# pyinstaller --onefile --windowed --icon=bird.png Warehouse\ GUI\ APP.py