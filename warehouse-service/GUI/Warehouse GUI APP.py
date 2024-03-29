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
        self.currentState = 'none'  # Track current state (items or products), initial state is 'none'
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setupFunctionBar(main_layout)
        self.setupItemDisplay(main_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setupFunctionBar(self, layout):
        self.function_layout = QHBoxLayout()
        self.function_layout.setAlignment(Qt.AlignLeft)

        self.buttons = {
            "Items": ("Items", self.readItems, 120),
            "Products": ("Products", self.readProducts, 120),
            "Create Item": ("Create Item", self.create, 120),
            "Create Product": ("Create Product", self.create, 120),
            "Details": ("Details", self.showDetails, 120),
            "Update": ("Update", self.update, 120),
            "Delete": ("Delete", self.delete, 120)
        }

        self.updateButtons()

        layout.addLayout(self.function_layout)
    
    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def updateButtons(self):
        self.clearLayout(self.function_layout)

        if self.currentState == 'items':
            button_set = ['Items', 'Products', 'Create Item', 'Details', 'Update', 'Delete']
        elif self.currentState == 'products':
            button_set = ['Items', 'Products', 'Create Product', 'Details', 'Update', 'Delete']
        else:  # self.currentState == 'none'
            button_set = ['Items', 'Products']

        for key in button_set:
            text, handler, width = self.buttons[key]
            button = QPushButton(text)
            button.clicked.connect(handler)
            button.setFixedSize(width, 40)
            
            # Apply base style
            button.setStyleSheet("""
                QPushButton {
                    background-color: #171720;
                    margin-right: 10px;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1E1E2A;
                }
                QPushButton:pressed {
                    background-color: #0D0D14;
                }
            """)

            # Highlight the button for the currently active list
            if (self.currentState == 'items' and text == 'Items') or \
            (self.currentState == 'products' and text == 'Products'):
                button.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    margin-right: 10px;
                    color: #aaffaa ;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1E1E2A;
                }
                QPushButton:pressed {
                    background-color: #0D0D14;
                }
            """)

            # Specific style for delete buttons
            if 'Delete' in text:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #8B0000;
                        margin-right: 10px;
                        color: white;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #A30000;
                    }
                    QPushButton:pressed {
                        background-color: #4D0000;
                    }
                """)

            self.function_layout.addWidget(button)

    def setupItemDisplay(self, layout):
        self.scrollArea = QScrollArea(self)
        self.scrollWidget = QWidget()
        self.scrollLayout = QVBoxLayout(self.scrollWidget)
        self.scrollLayout.setAlignment(Qt.AlignTop)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)
        layout.addWidget(self.scrollArea)

    def readItems(self):
        self.currentState = 'items'
        self.updateButtons()
        try:
            response = requests.get('http://127.0.0.1:8000/items/')
            if response.status_code == 200:
                self.current_items = response.json()
                self.clearLayout(self.scrollLayout)
                self.displayItems(self.current_items)
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch items from the server.")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def readProducts(self):
        self.currentState = 'products'
        self.updateButtons()
        try:
            response = requests.get('http://127.0.0.1:8000/products/')
            if response.status_code == 200:
                self.current_products = response.json()
                self.clearLayout(self.scrollLayout)
                self.displayItems(self.current_products)
            else:
                QMessageBox.warning(self, "Error", "Failed to fetch products from the server.")
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

    def displayProducts(self, products):
        header_labels = ["Select", "ID", "Name", "Quantity", "Description"]
        self.addHeaderRow(header_labels)
        self.checkboxes.clear()  # Clear the list of checkboxes for new products

        is_even = False
        for product in products:
            self.addProductRow(product, is_even)
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
        
    def addProductRow(self, product_data, is_even):
        row_layout = QHBoxLayout()
        checkbox = QCheckBox()
        self.checkboxes.append((checkbox, product_data['id'], product_data['name']))  # Store the checkbox, product's ID, and name
        checkbox.setFixedSize(60, 20)
        row_layout.addWidget(checkbox)

        details = [product_data.get('id'), product_data.get('name'), product_data.get('quantity'), product_data.get('description')]
        widths = [60, 200, 100, 300]
        for detail, width in zip(details, widths):
            label = QLabel(str(detail))
            label.setFixedSize(width, 20)
            bgColor = '#333333' if is_even else '#444444'
            label.setStyleSheet(f"background-color: {bgColor}; color: white;")
            row_layout.addWidget(label)

        self.scrollLayout.addLayout(row_layout)
    
    def create(self):
        if self.currentState == 'items':
            self.createItem()
        elif self.currentState == 'products':
            self.createProduct()
    
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
    
    def createProduct(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Product")
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
        save_button.clicked.connect(lambda: self.saveNewProduct(name_edit.text(), quantity_edit.text(), description_edit.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()
    
    def showDetails(self):
        if self.currentState == 'items':
            self.showItemDetails()
        elif self.currentState == 'products':
            self.showProductDetails()
            
    def showItemDetails(self):
        selected_items = [(checkbox, item_id) for checkbox, item_id, _ in self.checkboxes if checkbox.isChecked()]
        if len(selected_items) != 1:
            QMessageBox.warning(self, "Error", "Please select exactly one item to view details.")
            return

        item_id = selected_items[0][1]
        for item in self.current_items:
            if item['id'] == item_id:
                details = f"Name: {item['name']}\nQuantity: {item['quantity']}\nDescription: {item['description']}\n\nMore details here..."
                QMessageBox.information(self, "Item Details", details)
                break
            
    def showProductDetails(self):
        selected_products = [(checkbox, product_id) for checkbox, product_id, _ in self.checkboxes if checkbox.isChecked()]
        if len(selected_products) != 1:
            QMessageBox.warning(self, "Error", "Please select exactly one product to view details.")
            return

        product_id = selected_products[0][1]
        for product in self.current_products:
            if product['id'] == product_id:
                details = f"Name: {product['name']}\nQuantity: {product['quantity']}\nDescription: {product['description']}\n\nMore details here..."
                QMessageBox.information(self, "Product Details", details)
                break
    
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
    
    def saveNewProduct(self, name, quantity, description, dialog):
        if name and quantity and description:
            try:
                quantity = int(quantity)  # Ensure quantity is an integer
                data = {'name': name, 'quantity': quantity, 'description': description}

                response = requests.post('http://127.0.0.1:8000/products/', json=data)
                if response.status_code in [200, 201]:
                    dialog.accept()
                    self.readProducts()  # Refresh the product list
                else:
                    QMessageBox.warning(self, "Error", f"Failed to add the product. {response.text}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be an integer.")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "All fields are required.")
    
    def delete(self):
        if self.currentState == 'items':
            self.deleteItem()
        elif self.currentState == 'products':
            self.deleteProduct()
    
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
        delete_button.clicked.connect(lambda: self.confirmItemDeletion(selected_items, confirm_edit.text(), dialog))
        button_box.addWidget(delete_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def deleteProduct(self):
        selected_products = [(checkbox, product_id, name) for checkbox, product_id, name in self.checkboxes if checkbox.isChecked()]
        if not selected_products:
            QMessageBox.warning(self, "Error", "No products selected for deletion.")
            return

        product_list = '\n'.join([name for _, _, name in selected_products])
        confirm_msg = f"You are about to delete the following products:\n\n{product_list}\n\nType 'delete' to confirm:"

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Delete")
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel(confirm_msg))

        confirm_edit = QLineEdit()
        layout.addWidget(confirm_edit)

        button_box = QHBoxLayout()
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(lambda: self.confirmProductDeletion(selected_products, confirm_edit.text(), dialog))
        button_box.addWidget(delete_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(cancel_button)

        layout.addLayout(button_box)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def confirmItemDeletion(self, selected_items, typed_text, dialog):
        if typed_text.lower() == "delete":
            for _, item_id, _ in selected_items:
                response = requests.delete(f'http://127.0.0.1:8000/items/{item_id}')
                if response.status_code not in [200, 204]:
                    QMessageBox.warning(self, "Error", f"Failed to delete item. {response.text}")
            dialog.accept()
            self.readItems()  # Refresh the item list after deletion
        else:
            QMessageBox.warning(self, "Error", "Deletion canceled. You must type 'delete' to confirm.")
    
    def confirmProductDeletion(self, selected_products, typed_text, dialog):
        if typed_text.lower() == "delete":
            for _, product_id, _ in selected_products:
                response = requests.delete(f'http://127.0.0.1:8000/products/{product_id}')
                if response.status_code not in [200, 204]:
                    QMessageBox.warning(self, "Error", f"Failed to delete product. {response.text}")
            dialog.accept()
            self.readProducts()  # Refresh the product list after deletion
        else:
            QMessageBox.warning(self, "Error", "Deletion canceled. You must type 'delete' to confirm.")
    
    def update(self):
        if self.currentState == 'items':
            self.updateItem()
        elif self.currentState == 'products':
            self.updateProduct()
    
    def updateItem(self):
        selected_items = [(checkbox, item_id) for checkbox, item_id, _ in self.checkboxes if checkbox.isChecked()]
        if len(selected_items) != 1:
            QMessageBox.warning(self, "Error", "Please select exactly one item to update.")
            return

        _, item_id = selected_items[0]
        for item in self.current_items:  # Assume self.current_items stores the latest fetched list of items
            if item['id'] == item_id:
                self.showUpdateItemDialog(item)
                break

    def updateProduct(self):
        selected_products = [(checkbox, product_id) for checkbox, product_id, _ in self.checkboxes if checkbox.isChecked()]
        if len(selected_products) != 1:
            QMessageBox.warning(self, "Error", "Please select exactly one product to update.")
            return

        _, product_id = selected_products[0]
        for product in self.current_products:  # Assume self.current_products stores the latest fetched list of products
            if product['id'] == product_id:
                self.showUpdateProductDialog(product)
                break
            
    def showUpdateItemDialog(self, item):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Item")
        layout = QVBoxLayout()

        name_edit = QLineEdit(item['name'])
        quantity_edit = QLineEdit(str(item['quantity']))
        description_edit = QLineEdit(item['description'])

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(quantity_edit)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(description_edit)

        save_button = QPushButton("Update")
        save_button.clicked.connect(lambda: self.saveUpdatedItem(item['id'], name_edit.text(), quantity_edit.text(), description_edit.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def showUpdateProductDialog(self, product):
        dialog = QDialog(self)
        dialog.setWindowTitle("Update Product")
        layout = QVBoxLayout()

        name_edit = QLineEdit(product['name'])
        quantity_edit = QLineEdit(str(product['quantity']))
        description_edit = QLineEdit(product['description'])

        layout.addWidget(QLabel("Name:"))
        layout.addWidget(name_edit)
        layout.addWidget(QLabel("Quantity:"))
        layout.addWidget(quantity_edit)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(description_edit)

        save_button = QPushButton("Update")
        save_button.clicked.connect(lambda: self.saveUpdatedProduct(product['id'], name_edit.text(), quantity_edit.text(), description_edit.text(), dialog))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec_()
        
    def saveUpdatedItem(self, item_id, name, quantity, description, dialog):
        if name and quantity and description:
            try:
                quantity = int(quantity)  # Ensure quantity is an integer
                data = {'name': name, 'quantity': quantity, 'description': description}

                response = requests.put(f'http://127.0.0.1:8000/items/{item_id}', json=data)
                if response.status_code in [200, 204]:
                    dialog.accept()
                    self.readItems()  # Refresh the item list
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update the item. {response.text}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be an integer.")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "All fields are required.")

    def saveUpdatedProduct(self, product_id, name, quantity, description, dialog):
        if name and quantity and description:
            try:
                quantity = int(quantity)  # Ensure quantity is an integer
                data = {'name': name, 'quantity': quantity, 'description': description}

                response = requests.put(f'http://127.0.0.1:8000/products/{product_id}', json=data)
                if response.status_code in [200, 204]:
                    dialog.accept()
                    self.readProducts()  # Refresh the product list
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update the product. {response.text}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Quantity must be an integer.")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "All fields are required.")
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = InventoryApp()
    mainWin.show()
    sys.exit(app.exec_())


# make apk file
# pyinstaller --onefile --windowed --icon=bird.png Warehouse\ GUI\ APP.py