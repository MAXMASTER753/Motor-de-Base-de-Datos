import json

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtWidgets import QSplitter, QWidget
from PyQt6.QtCore import Qt

from engine.bplustree import BPlusTree
from gui.record_dialog import RecordDialog
from gui.schema_dialog import SchemaDialog

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
        self.showMaximized()
    #    self.setMinimumSize(900, 600)

        self.current_database_path = None

        self.index = BPlusTree(order=4)

        # =================================================
        # LAYOUT PRINCIPAL
        # =================================================

        self.main_layout = QVBoxLayout()

        self.splitter = QSplitter(Qt.Orientation.Horizontal)

        # =================================================
        # SIDEBAR IZQUIERDO
        # =================================================

        self.sidebar_layout = QVBoxLayout()

        # título
        self.sidebar_title = QLabel("Bases de Datos")
        self.sidebar_layout.addWidget(self.sidebar_title)

        # lista de bases
        self.database_list = QListWidget()
        self.database_list.itemDoubleClicked.connect(
            self.open_database
        )
        self.sidebar_layout.addWidget(self.database_list)

        # botones bases
        self.create_db_button = QPushButton("Crear Base")
        self.create_db_button.clicked.connect(self.create_database)

        self.delete_db_button = QPushButton("Eliminar Base")
        self.delete_db_button.clicked.connect(self.delete_database)

        self.open_button = QPushButton("Abrir Base")
        self.open_button.clicked.connect(self.open_database)

        self.sidebar_layout.addWidget(self.create_db_button)
        self.sidebar_layout.addWidget(self.delete_db_button)
        self.sidebar_layout.addWidget(self.open_button)

        # =================================================
        # PANEL DERECHO
        # =================================================

        self.right_layout = QVBoxLayout()

        # =============================================
        # BÚSQUEDA
        # =============================================

        self.search_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(
            self.search_record
        )
        self.search_input.setPlaceholderText("Buscar por ID")

        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.search_record)

        self.search_layout.addWidget(self.search_input)
        self.search_layout.addWidget(self.search_button)

        self.right_layout.addLayout(self.search_layout)

        # =============================================
        # TABLA
        # =============================================

        self.table = QTableWidget()

        # deshabilitar edición directa
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.right_layout.addWidget(self.table)

        # =============================================
        # CRUD
        # =============================================

        self.crud_layout = QHBoxLayout()

        self.add_button = QPushButton("Agregar Registro")
        self.add_button.clicked.connect(self.add_record)

        self.edit_button = QPushButton("Editar Registro")
        self.edit_button.clicked.connect(self.edit_record)

        self.delete_button = QPushButton("Eliminar Registro")
        self.delete_button.clicked.connect(self.delete_record)

        self.save_button = QPushButton("Guardar Cambios")
        self.save_button.clicked.connect(self.save_database)

        self.crud_layout.addWidget(self.add_button)
        self.crud_layout.addWidget(self.edit_button)
        self.crud_layout.addWidget(self.delete_button)
        self.crud_layout.addWidget(self.save_button)

        self.right_layout.addLayout(self.crud_layout)

        # =================================================
        # UNIR PANELES
        # =================================================

        # =================================================
        # CONTENEDOR SIDEBAR
        # =================================================

        self.sidebar_widget = QWidget()
        self.sidebar_widget.setLayout(self.sidebar_layout)

        # =================================================
        # CONTENEDOR DERECHO
        # =================================================

        self.right_widget = QWidget()
        self.right_widget.setLayout(self.right_layout)

        # =================================================
        # SPLITTER
        # =================================================

        self.splitter.addWidget(self.sidebar_widget)
        self.splitter.addWidget(self.right_widget)

        # tamaños iniciales
        self.splitter.setSizes([250, 950])

        self.main_layout.addWidget(self.splitter)

        self.setLayout(self.main_layout)

        # =================================================
        # CARGAR BASES
        # =================================================

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

        # =============================================
        # PREGUNTAR SI GUARDAR
        # =============================================

        if self.current_database_path is not None:

            reply = QMessageBox.question(
                self,
                "Cambiar Base de Datos",
                (
                    "¿Deseas guardar los cambios "
                    "antes de cambiar de base de datos?"
                ),
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return

            if reply == QMessageBox.StandardButton.Yes:
                self.save_database()

        # =============================================
        # ABRIR JSON
        # =============================================

        db_name = selected.text()

        path = DATABASES_DIR / db_name

        self.current_database_path = path

        

        try:

            with open(path, "r", encoding="utf-8") as file:
                database = json.load(file)

            # =================================================
            # COMPATIBILIDAD FORMATO NORMAL
            # =================================================

            if isinstance(database, list):

                data = database

                # generar schema automáticamente
                columns = []

                if data:

                    first_record = data[0]

                    for key in first_record.keys():

                        columns.append({
                            "name": key,
                            "type": "str",
                            "primary": len(columns) == 0
                        })

                schema = {
                    "columns": columns
                }

            # =================================================
            # FORMATO PROPIO
            # =================================================

            else:

                schema = database.get("schema", {})
                data = database.get("data", [])


            self.current_schema = schema

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo abrir:\n{e}"
            )

            return

        # =============================================
        # LIMPIAR TABLA
        # =============================================

        self.table.clear()
        self.table.setRowCount(0)

        # =============================================
        # SIN DATOS
        # =============================================

        # =============================================
        # ORDENAR COLUMNAS
        # PRIMARY KEY SIEMPRE PRIMERA
        # =============================================

        schema_columns = schema.get("columns", [])

        primary_column = None
        other_columns = []

        for column in schema_columns:

            if column["primary"]:
                primary_column = column["name"]
            else:
                other_columns.append(column["name"])

        columns = []

        if primary_column is not None:
            columns.append(primary_column)

        columns.extend(other_columns)

        # configurar columnas aunque no existan datos
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # base vacía
        if not data:

            self.rebuild_index()
            return

        # =============================================
        # COLUMNAS
        # =============================================

        columns = list(data[0].keys())

        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)

        # =============================================
        # FILAS
        # =============================================

        for row_index, record in enumerate(data):

            self.table.insertRow(row_index)

            for column_index, column_name in enumerate(columns):

                value = str(record.get(column_name, ""))

                item = QTableWidgetItem(value)

                self.table.setItem(
                    row_index,
                    column_index,
                    item
                )

        # =============================================
        # RECONSTRUIR ÍNDICE
        # =============================================

        self.rebuild_index()

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
            # AUTOINCREMENT
            # =============================================

            try:

                key = int(key)

            except:

                # buscar último ID
                max_id = 0

                for current_row in range(self.table.rowCount()):

                    item = self.table.item(current_row, 0)

                    if item is None:
                        continue

                    try:

                        current_id = int(item.text())

                        if current_id > max_id:
                            max_id = current_id

                    except:
                        continue

                key = max_id + 1

                # actualizar record
                record[primary_key] = key

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
                    continue

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
                "Selecciona un registro."
            )

            return

        # =============================================
        # OBTENER ID
        # =============================================

        item = self.table.item(current_row, 0)

        record_id = "?"

        if item is not None:
            record_id = item.text()

        # =============================================
        # CONFIRMACIÓN
        # =============================================

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            (
                f"¿Seguro que deseas eliminar el registro "
                f"con ID '{record_id}'?\n\n"
                f"Esta acción no se puede deshacer."
            ),
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # =============================================
        # PRIMARY KEY
        # =============================================

        item = self.table.item(current_row, 0)

        if item is not None:

            try:
                key = int(item.text())

            except:
                key = item.text()

        else:
            key = None

        # =============================================
        # ELIMINAR DEL ÍNDICE
        # =============================================

        self.index.delete(key, current_row)

        # =============================================
        # ELIMINAR FILA
        # =============================================

        self.table.removeRow(current_row)

        QMessageBox.information(
            self,
            "Eliminado",
            f"Registro '{record_id}' eliminado correctamente."
        )


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

        data = []

        # =============================================
        # OBTENER COLUMNAS
        # =============================================

        columns = []

        for column in range(self.table.columnCount()):

            header = self.table.horizontalHeaderItem(column)

            columns.append(header.text())

        # =============================================
        # OBTENER FILAS
        # =============================================

        for row in range(self.table.rowCount()):

            record = {}

            for column_index, column_name in enumerate(columns):

                item = self.table.item(row, column_index)

                value = ""

                if item is not None:
                    value = item.text()

                record[column_name] = value

            data.append(record)

        # =============================================
        # GUARDAR
        # =============================================

        database = {
            "schema": self.current_schema,
            "data": data
        }

        try:

            with open(
                self.current_database_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    database,
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

            # =============================================
            # OBTENER PRIMARY KEY
            # =============================================

            key_text = item.text().strip()

            # =============================================
            # VALIDAR ENTERO
            # =============================================

            try:
                key = int(key_text)

            except:

                # ignorar IDs inválidos
                continue

            # =============================================
            # INSERTAR EN B+ TREE
            # =============================================

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


    # =====================================================
    # CREAR BASE DE DATOS
    # =====================================================

    def create_database(self):

        name, ok = QInputDialog.getText(
            self,
            "Crear Base de Datos",
            "Nombre de la base:"
        )

        if not ok or name.strip() == "":
            return

        name = name.strip()

        if not name.endswith(".json"):
            name += ".json"

        path = DATABASES_DIR / name

        # =============================================
        # YA EXISTE
        # =============================================

        if path.exists():

            QMessageBox.warning(
                self,
                "Error",
                "La base de datos ya existe."
            )

            return

        # =============================================
        # DEFINIR SCHEMA
        # =============================================

        schema_dialog = SchemaDialog()

        if not schema_dialog.exec():
            return

        schema = schema_dialog.get_schema()

        # =============================================
        # CREAR ESTRUCTURA
        # =============================================

        database = {
            "schema": schema,
            "data": []
        }

        try:

            with open(path, "w", encoding="utf-8") as file:

                json.dump(
                    database,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo crear:\n{e}"
            )

            return

        self.load_databases()

        QMessageBox.information(
            self,
            "Creada",
            f"Base de datos '{name}' creada correctamente."
        )


    # =====================================================
    # ELIMINAR BASE DE DATOS
    # =====================================================

    def delete_database(self):

        selected = self.database_list.currentItem()

        if selected is None:

            QMessageBox.warning(
                self,
                "Error",
                "Selecciona una base de datos."
            )

            return

        db_name = selected.text()

        reply = QMessageBox.question(
            self,
            "Eliminar Base de Datos",
            (
                f"¿Seguro que deseas eliminar "
                f"la base de datos '{db_name}'?\n\n"
                f"Todos los registros se perderán.\n"
                f"Esta acción no se puede deshacer."
            ),
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        path = DATABASES_DIR / db_name

        try:

            path.unlink()

        except Exception as e:

            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo eliminar:\n{e}"
            )

            return

        self.load_databases()

        self.table.clear()

        QMessageBox.information(
            self,
            "Eliminada",
            f"Base de datos '{db_name}' eliminada."
        )