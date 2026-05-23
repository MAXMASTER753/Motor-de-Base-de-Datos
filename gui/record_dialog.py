from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox
)


class RecordDialog(QDialog):

    def __init__(self, columns, data=None):
        super().__init__()

        self.setWindowTitle("Registro")

        self.columns = columns
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

        for column, input_field in self.inputs.items():

            if input_field.text().strip() == "":

                QMessageBox.warning(
                    self,
                    "Error",
                    f"El campo '{column}' no puede estar vacío."
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

            # convertir automáticamente números
            try:

                if "." in value:
                    value = float(value)
                else:
                    value = int(value)

            except:
                pass

            record[column] = value

        return record