# tabs/color_mapping_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtSvgWidgets import QSvgWidget
from core.svg_color_scanner import SVGColorScanner
import os
import pandas as pd
from lxml import etree

class ColorRowWidget(QWidget):
    mapping_changed = pyqtSignal()

    def __init__(self, original_color, excel_columns, initial_mapping=""):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Color Preview
        self.color_box = QFrame()
        self.color_box.setFixedWidth(30)
        self.color_box.setFixedHeight(30)
        self.color_box.setStyleSheet(f"background-color: {original_color}; border: 1px solid #555; border-radius: 4px;")
        layout.addWidget(self.color_box)

        # Original Color Label
        self.color_label = QLabel(original_color)
        self.color_label.setFixedWidth(100)
        self.color_label.setFont(QLabel().font())
        layout.addWidget(self.color_label)

        layout.addWidget(QLabel("➡️ Map to Excel Column:"))

        # Excel Column Dropdown
        self.combo_column = QComboBox()
        self.combo_column.addItem("-- None --", "")
        for col in excel_columns:
            self.combo_column.addItem(col, col)
        
        if initial_mapping in excel_columns:
            self.combo_column.setCurrentText(initial_mapping)
            
        self.combo_column.currentIndexChanged.connect(lambda: self.mapping_changed.emit())
        layout.addWidget(self.combo_column, 1)

    def get_mapping(self):
        return self.combo_column.currentData()

class ColorMappingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.color_widgets = {}
        self.excel_columns = []
        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left Panel: Mappings
        left_panel = QWidget()
        left_panel.setMinimumWidth(350)
        left_layout = QVBoxLayout(left_panel)
        
        mapping_group = QGroupBox("🎨 Color Mapping")
        self.mapping_vbox = QVBoxLayout(mapping_group)
        
        # Scroll area for many colors
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(QWidget())
        self.scroll_layout = QVBoxLayout(self.scroll.widget())
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.mapping_vbox.addWidget(self.scroll)
        
        btn_scan = QPushButton("🔄 Scan SVG Colors")
        btn_scan.clicked.connect(self.refresh_colors)
        self.mapping_vbox.addWidget(btn_scan)
        
        left_layout.addWidget(mapping_group)
        splitter.addWidget(left_panel)
        
        # Right Panel: Preview
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        preview_group = QGroupBox("🔍 Preview (Using First Row of Excel)")
        preview_vbox = QVBoxLayout(preview_group)
        
        self.svg_preview = QSvgWidget()
        self.svg_preview.setMinimumSize(400, 300)
        preview_vbox.addWidget(self.svg_preview)
        
        btn_refresh_preview = QPushButton("🔄 Refresh Preview")
        btn_refresh_preview.clicked.connect(self.update_preview)
        preview_vbox.addWidget(btn_refresh_preview)
        
        right_layout.addWidget(preview_group)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

    def refresh_columns(self):
        """Update available excel columns from data_path"""
        from core.paths import resolve_path
        data_file = resolve_path(self.parent.generator_tab.data_path.text())
        if os.path.exists(data_file):
            try:
                df = pd.read_excel(data_file)
                self.excel_columns = df.columns.tolist()
                # Update existing combos
                for widget in self.color_widgets.values():
                    current = widget.get_mapping()
                    widget.combo_column.blockSignals(True)
                    widget.combo_column.clear()
                    widget.combo_column.addItem("-- None --", "")
                    for col in self.excel_columns:
                        widget.combo_column.addItem(col, col)
                    if current in self.excel_columns:
                        widget.combo_column.setCurrentText(current)
                    widget.combo_column.blockSignals(False)
            except:
                self.excel_columns = []

    def refresh_colors(self):
        from core.paths import resolve_path
        template_path = resolve_path(self.parent.generator_tab.template_path.text())
        if not os.path.exists(template_path):
            return

        self.refresh_columns()
        colors = SVGColorScanner.scan(template_path)
        
        # Clear old widgets
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
            
        self.color_widgets = {}
        
        # Load existing mappings from config if available
        existing_mappings = self.parent.config.get('color_mappings', {})
        
        for color in colors:
            widget = ColorRowWidget(color, self.excel_columns, existing_mappings.get(color, ""))
            widget.mapping_changed.connect(self.update_preview)
            self.scroll_layout.addWidget(widget)
            self.color_widgets[color] = widget
            
        self.update_preview()

    def update_preview(self):
        from core.paths import resolve_path
        template_path = resolve_path(self.parent.generator_tab.template_path.text())
        if not os.path.exists(template_path):
            return

        try:
            tree = etree.parse(template_path)
            root = tree.getroot()
            
            # Fetch data for preview
            row_data = {}
            data_file = resolve_path(self.parent.generator_tab.data_path.text())
            if os.path.exists(data_file):
                try:
                    df = pd.read_excel(data_file)
                    if not df.empty:
                        first_row = df.iloc[0]
                        for col in df.columns:
                            row_data[col.strip().lower()] = str(first_row[col])
                except: pass

            from core.generate import FlexibleGenerator
            config = self.parent.get_current_config()
            # The current state of mapping in the UI
            config['color_mappings'] = self.get_color_mappings()
            
            gen = FlexibleGenerator(config)
            # Use the generator logic to apply colors for preview
            # Note: Generator will need to be updated to handle color_mappings
            gen.replace_placeholders(root, pd.Series(row_data), config.get('field_mappings', {}))
            
            svg_data = etree.tostring(root, encoding='utf-8')
            self.svg_preview.load(svg_data)
        except Exception as e:
            print(f"Error updating preview: {e}")

    def get_color_mappings(self):
        mappings = {}
        for color, widget in self.color_widgets.items():
            col_name = widget.get_mapping()
            if col_name:
                mappings[color] = col_name
        return mappings

    def load_config(self, config):
        # We need to scan colors first to create widgets
        self.refresh_colors()
