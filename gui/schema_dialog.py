from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QCheckBox
)


class SchemaDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Definir Esquema")
        self.resize(700, 400)

        self.layout = QVBoxLayout()

        # =================================================
        # TABLA DE COLUMNAS
        # =================================================

        self.table = QTableWidget()

        self.table.setColumnCount(3)

        self.table.setHorizontalHeaderLabels([
            "Nombre",
            "Tipo",
            "Primary Key"
        ])

        self.layout.addWidget(self.table)

        # =================================================
        # BOTONES
        # =================================================

        self.buttons_layout = QHBoxLayout()

        self.add_column_button = QPushButton("Agregar Columna")
        self.add_column_button.clicked.connect(
            self.add_column
        )

        self.remove_column_button = QPushButton("Eliminar Columna")
        self.remove_column_button.clicked.connect(
            self.remove_column
        )

        self.save_button = QPushButton("Guardar Esquema")
        self.save_button.clicked.connect(
            self.validate_schema
        )

        self.buttons_layout.addWidget(
            self.add_column_button
        )

        self.buttons_layout.addWidget(
            self.remove_column_button
        )

        self.buttons_layout.addWidget(
            self.save_button
        )

        self.layout.addLayout(self.buttons_layout)

        self.setLayout(self.layout)

        # columna inicial
        self.add_column()

    # =====================================================
    # AGREGAR COLUMNA
    # =====================================================

    def add_column(self):

        row = self.table.rowCount()

        self.table.insertRow(row)

        # nombre
        name_input = QLineEdit()

        self.table.setCellWidget(
            row,
            0,
            name_input
        )

        # tipo
        type_combo = QComboBox()

        type_combo.addItems([
            "int",
            "float",
            "str"
        ])

        self.table.setCellWidget(
            row,
            1,
            type_combo
        )

        # primary key
        primary_checkbox = QCheckBox()

        self.table.setCellWidget(
            row,
            2,
            primary_checkbox
        )

    # =====================================================
    # ELIMINAR COLUMNA
    # =====================================================

    def remove_column(self):

        current_row = self.table.currentRow()

        if current_row >= 0:
            self.table.removeRow(current_row)

    
    # =====================================================
    # VALIDAR ESQUEMA
    # =====================================================

    def validate_schema(self):

        if self.table.rowCount() == 0:

            QMessageBox.warning(
                self,
                "Error",
                "Debe existir al menos una columna."
            )

            return

        primary_count = 0

        names = set()

        for row in range(self.table.rowCount()):

            name_widget = self.table.cellWidget(row, 0)
            type_widget = self.table.cellWidget(row, 1)
            primary_widget = self.table.cellWidget(row, 2)

            column_name = name_widget.text().strip()

            if column_name == "":

                QMessageBox.warning(
                    self,
                    "Error",
                    "Todas las columnas deben tener nombre."
                )

                return

            if column_name in names:

                QMessageBox.warning(
                    self,
                    "Error",
                    f"Columna duplicada: {column_name}"
                )

                return

            names.add(column_name)

            # ============================================
            # PRIMARY KEY
            # ============================================

            if primary_widget.isChecked():

                primary_count += 1

                # FORZAR INT
                if type_widget.currentText() != "int":

                    QMessageBox.warning(
                        self,
                        "Error",
                        (
                            "La Primary Key debe "
                            "ser de tipo int."
                        )
                    )

                    return

        if primary_count != 1:

            QMessageBox.warning(
                self,
                "Error",
                "Debe existir exactamente una primary key."
            )

            return

        self.accept()

    # =====================================================
    # OBTENER SCHEMA
    # =====================================================

    def get_schema(self):

        columns = []

        for row in range(self.table.rowCount()):

            name_widget = self.table.cellWidget(row, 0)
            type_widget = self.table.cellWidget(row, 1)
            primary_widget = self.table.cellWidget(row, 2)

            columns.append({
                "name": name_widget.text().strip(),
                "type": type_widget.currentText(),
                "primary": primary_widget.isChecked()
            })

        return {
            "columns": columns
        }