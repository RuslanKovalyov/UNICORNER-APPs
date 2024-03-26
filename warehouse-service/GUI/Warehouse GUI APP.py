import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox, QScrollArea
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setWindowIcon(QIcon('GUI.bird.png'))
        self.setGeometry(100, 100, 600, 400)  # Adjust the size as needed
        self.initUI()

    def initUI(self):
        # Create a layouts
        self.func_layout = QHBoxLayout() # layout for buttons
        self.layout = QVBoxLayout()      # main info layout

        # Button to create item
        self.createItemBtn = QPushButton("Create Item")
        self.createItemBtn.clicked.connect(self.createItem)
        self.createItemBtn.setFixedSize(100, 40)  # Set the size of the button
        self.func_layout.addWidget(self.createItemBtn)
        
        # Button to update item
        self.updateItemBtn = QPushButton("Update Item")
        self.updateItemBtn.clicked.connect(self.updateItem)
        self.updateItemBtn.setFixedSize(100, 40)
        self.func_layout.addWidget(self.updateItemBtn)
        
        # Button to delete item
        self.deleteItemBtn = QPushButton("Delete Item")
        self.deleteItemBtn.clicked.connect(self.deleteItem)
        self.deleteItemBtn.setFixedSize(100, 40)
        # dark red color
        self.deleteItemBtn.setStyleSheet("background-color: #8B0000; color: white;")
        self.func_layout.addWidget(self.deleteItemBtn)
        
        # Add the functions layout to the main layout
        self.layout.addLayout(self.func_layout)
        
        # Button to read items
        self.readItemsBtn = QPushButton("Read Items")
        self.readItemsBtn.clicked.connect(self.readItems)
        self.layout.addWidget(self.readItemsBtn)
        
        
        # Informative layout initialization
        global initInfoLayout
        def initInfoLayout():
            self.scrollArea = QScrollArea(self)
            self.scrollArea.setWidgetResizable(True)
            self.scrollWidget = QWidget()
            self.scrollLayout = QVBoxLayout()
            self.scrollWidget.setLayout(self.scrollLayout)
            self.scrollArea.setWidget(self.scrollWidget)
            self.layout.addWidget(self.scrollArea)
            container = QWidget()
            container.setLayout(self.layout)
            self.setCentralWidget(container)
            
        initInfoLayout()
        
        # make window size as 400X800
        self.setGeometry(400, 0, 900, 800)

    def readItems(self):
        try:
            response = requests.get('http://127.0.0.1:8000/items/')
            if response.status_code == 200:
                items = response.json()
                
                # if layout already has items, reinitalize the layout
                if self.scrollLayout.count() > 0:
                    self.scrollLayout.removeWidget(self.scrollArea)
                    self.scrollArea.deleteLater()
                    initInfoLayout()
                
                # column headers
                # itemLabel = QLabel(f"ID\t Name\t\t Quantity\t Description\n")
                # self.scrollLayout.addWidget(itemLabel)
                # make the columns as items of the layout
                self.item_layout = QHBoxLayout()
                lables = ["ID", "Name", "Quantity", "Description"]
                for lable in lables:
                    itemLabel = QLabel(f"{lable}")
                    # itemlabel as horizontal layout
                    itemLabel.setFixedSize(100, 20)
                    itemLabel.setStyleSheet("font-weight: bold;")         
                    self.item_layout.addWidget(itemLabel)
                    # make elements of item_layout left aligned
                self.scrollLayout.addLayout(self.item_layout)
                self.scrollLayout.setAlignment(self.item_layout, Qt.AlignLeft)
                
                self.scrollLayout.addWidget(QLabel("-" * 140))
                self.scrollLayout.setAlignment(Qt.AlignTop)
                

                # add items to the layout
                colored = False
                for item_id, item in items.items():
                    if colored:
                        colored = False
                    else:
                        colored = True
                    # itemLabel = QLabel(f"{item['id']}\t {item['name']}\t\t {item['quantity']}\t {item['description']}")
                    # self.scrollLayout.addWidget(itemLabel)
                    # create a horizontal layout for each item
                    self.item_layout = QHBoxLayout()
                    itemLabel = QLabel(f"{item['id']}")
                    itemLabel.setFixedSize(100, 20)
                    if colored:
                        itemLabel.setStyleSheet("background-color: #203040; color: white;")
                    self.item_layout.addWidget(itemLabel)
                    itemLabel = QLabel(f"{item['name']}")
                    itemLabel.setFixedSize(100, 20)
                    if colored:
                        itemLabel.setStyleSheet("background-color: #203040; color: white;")
                    self.item_layout.addWidget(itemLabel)
                    itemLabel = QLabel(f"{item['quantity']}")
                    itemLabel.setFixedSize(100, 20)
                    if colored:
                        itemLabel.setStyleSheet("background-color: #203040; color: white;")
                    self.item_layout.addWidget(itemLabel)
                    itemLabel = QLabel(f"{item['description']}")
                    itemLabel.setFixedSize(523, 20)
                    if colored:
                        itemLabel.setStyleSheet("background-color: #203040; color: white;")
                    self.item_layout.addWidget(itemLabel)

                    
                    self.scrollLayout.addLayout(self.item_layout)
                    self.scrollLayout.setAlignment(self.item_layout, Qt.AlignLeft)

                    
                self.scrollLayout.addWidget(QLabel(""))
                    
                
            else:
                QMessageBox.warning(self, "Error", "Could not fetch items from the backend.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def createItem(self):
        print("Create Item")
    
    def deleteItem(self):
        print("Delete Item")
    
    def updateItem(self):
        print("Update Item")
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InventoryApp()
    mainWin.show()
    sys.exit(app.exec_())


# make apk file
# pyinstaller --onefile --windowed --icon=bird.png Warehouse\ GUI\ APP.py