import sys
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox, QScrollArea, QCheckBox, QDialog, QLineEdit)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.setWindowIcon(QIcon('GUI.bird.png'))
        self.setGeometry(400, 100, 800, 600)
        self.checkboxes = []  # Keep track of checkboxes and their associated items
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setupFunctionBar(main_layout)
        self.setupItemDisplay(main_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setupFunctionBar(self, layout):
        function_layout = QHBoxLayout()
        function_layout.setAlignment(Qt.AlignLeft)

        buttons = [
            ("Read Items", self.readItems, 120),
            ("Create Item", self.createItem, 120),
            ("Update Item", self.updateItem, 120),
            ("Delete Item", self.deleteItem, 120)
        ]

        for text, handler, width in buttons:
            button = QPushButton(text)
            button.clicked.connect(handler)
            button.setFixedSize(width, 40)
            button.setStyleSheet("QPushButton {background-color: #171720; margin-right: 10px; color: white; border-radius: 5px;} QPushButton:hover {background-color: #1E1E2A;} QPushButton:pressed {background-color: #0D0D14;}")
            if text == "Delete Item":
                button.setStyleSheet("QPushButton {background-color: #8B0000; margin-right: 10px; color: white; border-radius: 5px;} QPushButton:hover {background-color: #A30000;} QPushButton:pressed {background-color: #4D0000;}")
            function_layout.addWidget(button)

        layout.addLayout(function_layout)

    def setupItemDisplay(self, layout):
        self.scrollArea = QScrollArea(self)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

    def readItems(self):
        try:
            response = requests.get('http://127.0.0.1:8000/items/')
            if response.status_code == 200:
                items = response.json()  # This should now be a list directly
                self.clearLayout(self.scrollLayout)
                self.displayItems(items)
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch items from the server.")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def displayItems(self, items):
        header_labels = ["Select", "ID", "Name", "Quantity", "Description"]
        self.addHeaderRow(header_labels)
        self.checkboxes.clear()  # Clear the list of checkboxes for new items

        is_even = False
        for item in items:
            self.addItemRow(item, is_even)
            is_even = not is_even

    def clearLayout(self, layout):
        while layout.count():
            layout_item = layout.takeAt(0)
            if layout_item.widget():
                layout_item.widget().deleteLater()
            elif layout_item.layout():
                self.clearLayout(layout_item.layout())
                layout_item.layout().deleteLater()

    def addHeaderRow(self, labels):
        header_layout = QHBoxLayout()
        widths = [60, 60, 200, 100, 300]
        for label, width in zip(labels, widths):
            lbl = QLabel(label)
            lbl.setFixedSize(width, 30)
            lbl.setStyleSheet("font-weight: bold; border: 1px solid #c0c0c0;")
            header_layout.addWidget(lbl)
        self.scrollLayout.addLayout(header_layout)
    
    def addItemRow(self, item_data, is_even):
        row_layout = QHBoxLayout()
        checkbox = QCheckBox()
        self.checkboxes.append((checkbox, item_data['id'], item_data['name']))  # Store the checkbox, item's ID, and name
        checkbox.setFixedSize(60, 20)
        row_layout.addWidget(checkbox)

        details = [item_data.get('id'), item_data.get('name'), item_data.get('quantity'), item_data.get('description')]
        widths = [60, 200, 100, 300]
        for detail, width in zip(details, widths):
            label = QLabel(str(detail))
            label.setFixedSize(width, 20)
            bgColor = '#333333' if is_even else '#444444'
            label.setStyleSheet(f"background-color: {bgColor}; color: white;")
            row_layout.addWidget(label)

        self.scrollLayout.addLayout(row_layout)
        
    def createItem(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Item")
        layout = QVBoxLayout()

        name_edit = QLineEdit()
        quantity_edit = QLineEdit()
        description_edit = QLineEdit()

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(quantity_edit)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(description_edit)

        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.saveNewItem(name_edit.text(), quantity_edit.text(), description_edit.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()
    
    def saveNewItem(self, name, quantity, description, dialog):
        if name and quantity and description:
            try:
                quantity = int(quantity)  # Ensure quantity is an integer
                data = {'name': name, 'quantity': quantity, 'description': description}

                response = requests.post('http://127.0.0.1:8000/items/', json=data)
                if response.status_code in [200, 201]:
                    dialog.accept()
                    self.readItems()  # Refresh the item list
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add the item. {response.text}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be an integer.")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "All fields are required.")
    
    def deleteItem(self):
        selected_items = [(checkbox, item_id, name) for checkbox, item_id, name in self.checkboxes if checkbox.isChecked()]
        if not selected_items:
            QMessageBox.warning(self, "Error", "No items selected for deletion.")
            return

        item_list = '\n'.join([name for _, _, name in selected_items])
        confirm_msg = f"You are about to delete the following items:\n\n{item_list}\n\nType 'delete' to confirm:"

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Delete")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(confirm_msg))

        confirm_edit = QLineEdit()
        layout.addWidget(confirm_edit)

        button_box = QHBoxLayout()
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.confirmDeletion(selected_items, confirm_edit.text(), dialog))
        button_box.addWidget(delete_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)
        dialog.setLayout(layout)
        dialog.exec_()

    def confirmDeletion(self, selected_items, typed_text, dialog):
        if typed_text.lower() == "delete":
            for _, item_id, _ in selected_items:
                response = requests.delete(f'http://127.0.0.1:8000/items/{item_id}')
                if response.status_code not in [200, 204]:
                    QMessageBox.warning(self, "Error", f"Failed to delete item. {response.text}")
            dialog.accept()
            self.readItems()  # Refresh the item list after deletion
        else:
            QMessageBox.warning(self, "Error", "Deletion canceled. You must type 'delete' to confirm.")
    
    def updateItem(self):
        print("Update Item")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InventoryApp()
    mainWin.show()
    sys.exit(app.exec_())



# make apk file
# pyinstaller --onefile --windowed --icon=bird.png Warehouse\ GUI\ APP.py