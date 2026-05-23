import json

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem
)


DATABASES_DIR = Path("databases")


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mini Database Engine")
        self.resize(800, 600)

        self.layout = QVBoxLayout()

        # =================================================
        # TÍTULO
        # =================================================

        self.title = QLabel("Bases de Datos JSON")
        self.layout.addWidget(self.title)

        # =================================================
        # LISTA DE BASES
        # =================================================

        self.database_list = QListWidget()
        self.layout.addWidget(self.database_list)

        # =================================================
        # BOTÓN ABRIR
        # =================================================

        self.open_button = QPushButton("Abrir Base de Datos")
        self.open_button.clicked.connect(self.open_database)

        self.layout.addWidget(self.open_button)

        # =================================================
        # TABLA
        # =================================================

        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.load_databases()

    # =====================================================
    # CARGAR BASES DE DATOS
    # =====================================================

    def load_databases(self):

        self.database_list.clear()

        DATABASES_DIR.mkdir(exist_ok=True)

        json_files = sorted(DATABASES_DIR.glob("*.json"))

        for file in json_files:
            self.database_list.addItem(file.name)

    # =====================================================
    # ABRIR BASE DE DATOS
    # =====================================================

    def open_database(self):

        selected = self.database_list.currentItem()

        if selected is None:
            QMessageBox.warning(
                self,
                "Error",
                "Selecciona una base de datos."
            )
            return

        db_name = selected.text()

        db_path = DATABASES_DIR / db_name

        try:

            with open(db_path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir el archivo:\n{e}"
            )

            return

        # =================================================
        # VALIDAR JSON
        # =================================================

        if not isinstance(data, list):

            QMessageBox.warning(
                self,
                "Error",
                "El JSON debe contener una lista de registros."
            )

            return

        if len(data) == 0:

            self.table.clear()

            QMessageBox.information(
                self,
                "Vacío",
                "La base de datos está vacía."
            )

            return

        # =================================================
        # DETECTAR COLUMNAS
        # =================================================

        columns = list(data[0].keys())

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        self.table.setRowCount(len(data))

        # =================================================
        # LLENAR TABLA
        # =================================================

        for row_index, record in enumerate(data):

            for column_index, column_name in enumerate(columns):

                value = str(record.get(column_name, ""))

                item = QTableWidgetItem(value)

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

        QMessageBox.information(
            self,
            "Base de Datos Abierta",
            f"{db_name} cargada correctamente."
        )