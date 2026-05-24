from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox
)


class RecordDialog(QDialog):

    def __init__(self, columns, schema=None, data=None):
        super().__init__()

        self.setWindowTitle("Registro")

        self.columns = columns
        self.schema = schema or {}
        self.inputs = {}

        self.layout = QVBoxLayout()

        # ============================================
        # FORMULARIO
        # ============================================

        self.form_layout = QFormLayout()

        for column in columns:

            line_edit = QLineEdit()

            # si estamos editando
            if data and column in data:
                line_edit.setText(str(data[column]))

            self.inputs[column] = line_edit

            self.form_layout.addRow(column, line_edit)

        self.layout.addLayout(self.form_layout)

        # ============================================
        # BOTÓN GUARDAR
        # ============================================

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.validate)

        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    # =================================================
    # VALIDAR DATOS
    # =================================================

    def validate(self):

        primary_found = False

        for column, input_field in self.inputs.items():

            value = input_field.text().strip()

            # buscar metadata de columna
            column_schema = None

            for col in self.schema.get("columns", []):

                if col["name"] == column:
                    column_schema = col
                    break

            if column_schema is None:
                continue

            column_type = column_schema["type"]
            is_primary = column_schema["primary"]

            # =========================================
            # PRIMARY KEY AUTOINCREMENT
            # =========================================

            if is_primary:

                primary_found = True

                # vacío -> permitido (autoincrement)
                if value == "":
                    continue

                # debe ser entero
                try:
                    int(value)

                except:

                    QMessageBox.warning(
                        self,
                        "Error",
                        (
                            f"La Primary Key '{column}' "
                            f"debe ser numérica."
                        )
                    )

                    return

                # debe ser entero
                try:
                    int(value)
                except:

                    QMessageBox.warning(
                        self,
                        "Error",
                        (
                            f"La primary key '{column}' "
                            f"debe ser numérica."
                        )
                    )

                    return

            # =========================================
            # VALIDAR TIPOS
            # =========================================

            else:

                if value == "":
                    continue

                try:

                    # int
                    if column_type == "int":

                        int(value)

                    # float
                    elif column_type == "float":

                        float(value)

                    # str
                    elif column_type == "str":

                        str(value)

                except:

                    QMessageBox.warning(
                        self,
                        "Error",
                        (
                            f"'{column}' debe ser "
                            f"de tipo {column_type}."
                        )
                    )

                    return

        self.accept()

    # =================================================
    # OBTENER DATOS
    # =================================================

    def get_data(self):

        record = {}

        for column, input_field in self.inputs.items():

            value = input_field.text().strip()

            # buscar tipo
            column_schema = None

            for col in self.schema.get("columns", []):

                if col["name"] == column:
                    column_schema = col
                    break

            if column_schema is None:

                record[column] = value
                continue

            column_type = column_schema["type"]

            # =========================================
            # AUTO INCREMENT
            # =========================================

            if column_schema["primary"] and value == "":

                record[column] = None
                continue

            # =========================================
            # CASTING
            # =========================================

            if column_type == "int":
                value = int(value)

            elif column_type == "float":
                value = float(value)

            record[column] = value

        return record