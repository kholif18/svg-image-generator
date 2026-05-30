# widgets/field_widget.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from typing import Dict


class FieldConfigWidget(QWidget):
    """Widget untuk konfigurasi satu field (text atau image)"""
    field_removed = pyqtSignal(object)

    def __init__(self, field_data: Dict = None, index: int = 0):
        super().__init__()
        self.field_data = field_data or {}
        self.index = index
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Nomor field
        self.header_label = QLabel(f"#{self.index + 1}")
        self.header_label.setFixedWidth(30)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("""
            QLabel {
                color: #4ec9b0;
                font-weight: bold;
                font-size: 12px;
                background-color: #1e1e1e;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        main_layout.addWidget(self.header_label)

        # Tipe Field
        self.type_combo = QComboBox()
        self.type_combo.addItems(["📝 Text", "🖼️ Image"])
        current_type = self.field_data.get('type', 'text')
        self.type_combo.setCurrentText("📝 Text" if current_type == 'text' else "🖼️ Image")
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.type_combo.setFixedWidth(110)
        self.type_combo.setStyleSheet("""
            QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox:hover { border-color: #0e639c; }
        """)
        main_layout.addWidget(self.type_combo)

        # TEXT FIELD WIDGETS
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nama Field")
        self.name_edit.setText(self.field_data.get('name', ''))
        self.name_edit.setMinimumWidth(150)
        self.name_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.name_edit.setStyleSheet(self.get_edit_style())
        main_layout.addWidget(self.name_edit, 1)  # Stretch factor 1

        self.placeholder_edit = QLineEdit()
        self.placeholder_edit.setPlaceholderText("{{PLACEHOLDER}}")
        self.placeholder_edit.setText(self.field_data.get('placeholder', ''))
        self.placeholder_edit.setMinimumWidth(180)
        self.placeholder_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.placeholder_edit.setStyleSheet(self.get_edit_style())
        main_layout.addWidget(self.placeholder_edit, 1)  # Stretch factor 1

        # IMAGE FIELD WIDGETS
        self.column_edit = QLineEdit()
        self.column_edit.setPlaceholderText("Kolom Excel (sumber foto)")
        self.column_edit.setText(self.field_data.get('column', ''))
        self.column_edit.setMinimumWidth(150)
        self.column_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.column_edit.setStyleSheet(self.get_edit_style())
        main_layout.addWidget(self.column_edit, 1)  # Stretch factor 1

        self.image_id_edit = QLineEdit()
        self.image_id_edit.setPlaceholderText("Image ID di SVG")
        self.image_id_edit.setText(self.field_data.get('image_id', ''))
        self.image_id_edit.setMinimumWidth(150)
        self.image_id_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.image_id_edit.setStyleSheet(self.get_edit_style())
        main_layout.addWidget(self.image_id_edit, 1)  # Stretch factor 1

        # Tombol hapus
        self.remove_btn = QPushButton("🗑️")
        self.remove_btn.setFixedSize(45, 32)
        self.remove_btn.setToolTip("Hapus field ini")
        self.remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #e34d3d; }
            QPushButton:pressed { background-color: #a02010; }
        """)
        self.remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.remove_btn.clicked.connect(lambda: self.field_removed.emit(self))
        main_layout.addWidget(self.remove_btn)

        self.setLayout(main_layout)
        self.setStyleSheet("""
            FieldConfigWidget {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                border-radius: 8px;
            }
            FieldConfigWidget:hover { border-color: #0e639c; }
        """)

        self.on_type_changed(self.type_combo.currentText())

    def get_edit_style(self):
        return """
            QLineEdit {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 7px;
            }
            QLineEdit:focus { border-color: #0e639c; }
        """

    def on_type_changed(self, type_text):
        is_text = "text" in type_text.lower()
        
        # Text field widgets
        self.name_edit.setVisible(is_text)
        self.placeholder_edit.setVisible(is_text)
        
        # Image field widgets
        self.column_edit.setVisible(not is_text)
        self.image_id_edit.setVisible(not is_text)

    def get_config(self) -> Dict:
        type_text = self.type_combo.currentText().lower()
        is_text = "text" in type_text

        if is_text:
            name = self.name_edit.text().strip()
            return {
                'type': 'text',
                'name': name,
                'placeholder': self.placeholder_edit.text().strip() or f'{{{{{name}}}}}'
            }
        else:
            return {
                'type': 'image',
                'name': self.image_id_edit.text().strip(),
                'image_id': self.image_id_edit.text().strip(),
                'column': self.column_edit.text().strip()
            }
