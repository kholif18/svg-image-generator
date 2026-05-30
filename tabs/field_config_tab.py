# tabs/field_config_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from widgets.field_widget import FieldConfigWidget


class FieldConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.field_widgets = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # ========== PANDUAN / PETUNJUK ==========
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border-radius: 8px;
                border-left: 4px solid #0e639c;
            }
        """)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 12, 15, 12)

        info_text = QLabel(
            "📌 PANDUAN FIELD MAPPING\n"
            "┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈┈\n"
            "📝 TEXT FIELD : Nama Field → digunakan untuk mencocokkan data dari Excel | Placeholder di SVG → teks yang akan diganti (contoh: {{NAMA}})\n"
            "🖼️ IMAGE FIELD : Kolom Excel (sumber) → nama kolom di Excel yang berisi nama file foto | Image ID (tujuan) → ID element <image> di file SVG\n"
            "💡 Tips: Klik 'Add New Field' untuk menambah field, gunakan tombol 🗑️ (merah) untuk menghapus field"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("""
            QLabel {
                color: #d4d4d4;
                font-size: 11px;
                line-height: 1.5;
            }
        """)
        info_layout.addWidget(info_text)
        info_layout.addStretch()

        layout.addWidget(info_frame)

        # ========== HEADER KOLOM ==========
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 6px;
                margin-top: 5px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 8, 10, 8)
        header_layout.setSpacing(10)

        # # (lebar tetap 30)
        lbl_no = QLabel("#")
        lbl_no.setFixedWidth(30)
        lbl_no.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_no.setStyleSheet("color: #4ec9b0; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(lbl_no)

        # Tipe Field (lebar tetap 110)
        lbl_type = QLabel("Tipe Field")
        lbl_type.setFixedWidth(110)
        lbl_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_type.setStyleSheet("color: #4ec9b0; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(lbl_type)

        # Nama Field (stretch 1 - sama seperti field widget)
        lbl_text_field = QLabel("📝 Nama Field →")
        lbl_text_field.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_text_field.setStyleSheet("color: #6a9955; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(lbl_text_field, 1)

        # Placeholder di SVG (stretch 1)
        lbl_placeholder = QLabel("↓ Placeholder di SVG")
        lbl_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_placeholder.setStyleSheet("color: #6a9955; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(lbl_placeholder, 1)

        # Aksi (lebar tetap 36 - sama dengan tombol hapus)
        lbl_action = QLabel("Aksi")
        lbl_action.setFixedWidth(36)
        lbl_action.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_action.setStyleSheet("color: #f48771; font-weight: bold; font-size: 12px;")
        header_layout.addWidget(lbl_action)

        layout.addWidget(header_widget)

        # Garis pemisah
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3c3c3c; max-height: 1px; margin: 5px 0;")
        layout.addWidget(line)

        # ========== SCROLL AREA UNTUK FIELDS ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #2d2d2d;
                width: 10px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical {
                background: #0e639c;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #1177bb;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        layout.addWidget(scroll)

        self.fields_container = QWidget()
        self.fields_container.setStyleSheet("background-color: transparent;")
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setSpacing(8)
        self.fields_layout.setContentsMargins(0, 0, 0, 0)
        self.fields_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.fields_container)

        # ========== TOMBOL ADD FIELD ==========
        btn_add_layout = QHBoxLayout()
        btn_add_layout.addStretch()

        btn_add = QPushButton("➕ Add New Field")
        btn_add.setFixedWidth(200)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4f7a;
            }
        """)
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_field)
        btn_add_layout.addWidget(btn_add)
        
        btn_add_layout.addStretch()
        layout.addLayout(btn_add_layout)

    def add_field(self, field_data=None):
        widget = FieldConfigWidget(field_data, len(self.field_widgets))
        widget.field_removed.connect(self.remove_field)
        self.fields_layout.addWidget(widget)
        self.field_widgets.append(widget)
        for i, w in enumerate(self.field_widgets):
            w.header_label.setText(f"#{i + 1}")

    def remove_field(self, widget):
        if widget in self.field_widgets:
            self.field_widgets.remove(widget)
            widget.deleteLater()
            for i, w in enumerate(self.field_widgets):
                w.header_label.setText(f"#{i + 1}")

    def get_field_mappings(self):
        mappings = {}

        for widget in self.field_widgets:
            config = widget.get_config()

            if not isinstance(config, dict):
                continue

            name = config.get('name')

            if not name:
                continue

            mappings[name] = {
                k: v
                for k, v in config.items()
                if k != 'name'
            }

        return mappings

    def load_fields(self, config):
        # Clear existing
        for widget in self.field_widgets[:]:
            self.remove_field(widget)

        fields = config.get('field_mappings', [])
        if not fields:
            default_fields = []
            for field in default_fields:
                self.add_field(field)
        else:
            if isinstance(fields, dict):
                fields = list(fields.values())
            for field in fields:
                self.add_field(field)