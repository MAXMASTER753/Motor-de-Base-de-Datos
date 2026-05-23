import json

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QAbstractItemView

from engine.bplustree import BPlusTree
from gui.record_dialog import RecordDialog

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHBoxLayout
)


DATABASES_DIR = Path("databases")


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mini Database Engine")
        self.resize(900, 600)

        self.current_database_path = None

        self.index = BPlusTree(order=4)

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
        # BÚSQUEDA
        # =================================================

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por ID")

        self.layout.addWidget(self.search_input)

        self.search_button = QPushButton("Buscar Registro")
        self.search_button.clicked.connect(self.search_record)

        self.layout.addWidget(self.search_button)

        # =================================================
        # TABLA
        # =================================================

        self.table = QTableWidget()

        # deshabilitar edición directa
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        
        self.layout.addWidget(self.table)

        # =================================================
        # BOTONES CRUD
        # =================================================

        self.buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Agregar Registro")
        self.add_button.clicked.connect(self.add_record)

        self.edit_button = QPushButton("Editar Registro")
        self.edit_button.clicked.connect(self.edit_record) 

        self.delete_button = QPushButton("Eliminar Registro")
        self.delete_button.clicked.connect(self.delete_record)

        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.clicked.connect(self.save_database)

        self.buttons_layout.addWidget(self.add_button)
        self.buttons_layout.addWidget(self.edit_button)
        self.buttons_layout.addWidget(self.delete_button)
        self.buttons_layout.addWidget(self.save_button)

        self.layout.addLayout(self.buttons_layout)

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

        self.current_database_path = db_path

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

        if not isinstance(data, list):

            QMessageBox.warning(
                self,
                "Error",
                "El JSON debe contener una lista."
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

        columns = list(data[0].keys())

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        self.table.setRowCount(len(data))


        # reconstruir índice
        self.index = BPlusTree(order=4)

        for row_index, record in enumerate(data):

            # usar primera columna como primary key
            primary_key_column = columns[0]

            if primary_key_column in record:

                key = record[primary_key_column]

                # convertir números automáticamente
                try:
                    key = int(key)
                except:
                    pass

                self.index.insert(key, row_index)

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

    # =====================================================
    # AGREGAR REGISTRO
    # =====================================================

    def add_record(self):

        columns = []

        for column in range(self.table.columnCount()):

            header = self.table.horizontalHeaderItem(column)

            if header:
                columns.append(header.text())

        # no hay columnas
        if not columns:

            QMessageBox.warning(
                self,
                "Error",
                "Primero abre una base de datos."
            )

            return

        dialog = RecordDialog(columns)

        if dialog.exec():

            record = dialog.get_data()

            # =============================================
            # PRIMARY KEY
            # =============================================

            primary_key = columns[0]

            key = record[primary_key]

           

            # =============================================
            # INSERTAR EN TABLA
            # =============================================

            # =============================================
            # ENCONTRAR POSICIÓN ORDENADA
            # =============================================

            row = self.table.rowCount()

            insert_position = row

            for current_row in range(row):

                item = self.table.item(current_row, 0)

                if item is None:
                    continue

                current_key = item.text()

                try:
                    current_key = int(current_key)
                except:
                    pass

                if key < current_key:

                    insert_position = current_row
                    break

            # insertar fila ordenada
            self.table.insertRow(insert_position)

            for column_index, column_name in enumerate(columns):

                value = str(record.get(column_name, ""))

                item = QTableWidgetItem(value)

                self.table.setItem(
                    insert_position,
                    column_index,
                    item
                )

            # =============================================
            # ACTUALIZAR ÍNDICE
            # =============================================

            self.rebuild_index()

            QMessageBox.information(
                self,
                "Insertado",
                f"Registro con clave '{key}' insertado correctamente."
            )

    # =====================================================
    # ELIMINAR REGISTRO
    # =====================================================

    def delete_record(self):

        current_row = self.table.currentRow()

        if current_row < 0:

            QMessageBox.warning(
                self,
                "Error",
                "Selecciona una fila."
            )

            return

        self.table.removeRow(current_row)
        self.rebuild_index()

    # =====================================================
    # GUARDAR BASE DE DATOS
    # =====================================================

    def save_database(self):

        if self.current_database_path is None:

            QMessageBox.warning(
                self,
                "Error",
                "No hay base de datos abierta."
            )

            return

        rows = self.table.rowCount()
        columns = self.table.columnCount()

        headers = []

        for column in range(columns):

            header = self.table.horizontalHeaderItem(column).text()

            headers.append(header)

        data = []

        for row in range(rows):

            record = {}

            for column in range(columns):

                item = self.table.item(row, column)

                value = ""

                if item is not None:
                    value = item.text()

                record[headers[column]] = value

            data.append(record)

        try:

            with open(
                self.current_database_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo guardar:\n{e}"
            )

            return

        QMessageBox.information(
            self,
            "Guardado",
            "Base de datos guardada correctamente."
        )

    # =====================================================
    # BUSCAR REGISTRO
    # =====================================================

    def search_record(self):

        text = self.search_input.text().strip()

        if text == "":

            QMessageBox.warning(
                self,
                "Error",
                "Ingresa un ID."
            )

            return

        try:
            key = int(text)

        except:

            QMessageBox.warning(
                self,
                "Error",
                "El ID debe ser numérico."
            )

            return

        rows = self.index.search_all(key)

        if not rows:

            QMessageBox.information(
                self,
                "No encontrado",
                f"No existe id={key}"
            )

            return

        self.table.clearSelection()

        for row in rows:
            self.table.selectRow(row)

        QMessageBox.information(
            self,
            "Encontrado",
            f"{len(rows)} registro(s) encontrados."
        )

    # =====================================================
    # RECONSTRUIR ÍNDICE
    # =====================================================

    def rebuild_index(self):

        self.index = BPlusTree(order=4)

        rows = self.table.rowCount()

        if self.table.columnCount() == 0:
            return

        primary_key_column = 0

        for row in range(rows):

            item = self.table.item(row, primary_key_column)

            if item is None:
                continue

            key = item.text()

            # convertir números
            try:
                key = int(key)
            except:
                pass

            self.index.insert(key, row)


    # =====================================================
    # EDITAR REGISTRO
    # =====================================================

    def edit_record(self):

        current_row = self.table.currentRow()

        if current_row < 0:

            QMessageBox.warning(
                self,
                "Error",
                "Selecciona un registro."
            )

            return

        # =============================================
        # OBTENER COLUMNAS
        # =============================================

        columns = []

        for column in range(self.table.columnCount()):

            header = self.table.horizontalHeaderItem(column)

            if header:
                columns.append(header.text())

        # =============================================
        # OBTENER DATOS ACTUALES
        # =============================================

        current_data = {}

        for column_index, column_name in enumerate(columns):

            item = self.table.item(current_row, column_index)

            value = ""

            if item is not None:
                value = item.text()

            current_data[column_name] = value

        # =============================================
        # ABRIR DIÁLOGO
        # =============================================

        dialog = RecordDialog(columns, current_data)

        if dialog.exec():

            updated_record = dialog.get_data()

            # =========================================
            # ACTUALIZAR TABLA
            # =========================================

            for column_index, column_name in enumerate(columns):

                value = str(updated_record[column_name])

                item = QTableWidgetItem(value)

                self.table.setItem(
                    current_row,
                    column_index,
                    item
                )

            # =========================================
            # REORDENAR TABLA
            # =========================================

            self.sort_table()

            # =========================================
            # RECONSTRUIR ÍNDICE
            # =========================================

            self.rebuild_index()

            QMessageBox.information(
                self,
                "Actualizado",
                "Registro actualizado correctamente."
            )


    # =====================================================
    # ORDENAR TABLA
    # =====================================================

    def sort_table(self):

        rows = []

        row_count = self.table.rowCount()
        column_count = self.table.columnCount()

        # extraer datos
        for row in range(row_count):

            record = []

            for column in range(column_count):

                item = self.table.item(row, column)

                value = ""

                if item is not None:
                    value = item.text()

                record.append(value)

            rows.append(record)

        # ordenar por primera columna
        def sort_key(record):

            try:
                return int(record[0])
            except:
                return record[0]

        rows.sort(key=sort_key)

        # limpiar tabla
        self.table.setRowCount(0)

        # reinsertar ordenado
        for row_data in rows:

            row_position = self.table.rowCount()

            self.table.insertRow(row_position)

            for column, value in enumerate(row_data):

                self.table.setItem(
                    row_position,
                    column,
                    QTableWidgetItem(str(value))
                )