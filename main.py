# main.py
import sys
import os
import json
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from tabs import GeneratorTab, FieldConfigTab, OutputTab, ColorMappingTab
from core.paths import app_path, ensure_portable_env, find_inkscape, relative_to_app


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize portable environment
        ensure_portable_env()
        
        self.config_file = app_path("config", "default.json")
        self.config = {}
        self.initUI()
        self.load_config()

    def initUI(self):
        self.setWindowTitle("Flexible SVG/Image Generator (Portable)")
        self.setGeometry(100, 100, 1200, 800)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Tab 1: Generator
        self.generator_tab = GeneratorTab(self)
        tabs.addTab(self.generator_tab, "🚀 Generator")

        # Tab 2: Color Mapping
        self.color_mapping_tab = ColorMappingTab(self)
        tabs.addTab(self.color_mapping_tab, "🎨 Color Mapping")

        # Tab 3: Field Configuration
        self.field_config_tab = FieldConfigTab(self)
        tabs.addTab(self.field_config_tab, "📝 Field Configuration")

        # Tab 4: Output Settings
        self.output_tab = OutputTab(self)
        tabs.addTab(self.output_tab, "💾 Output Settings")

        # Connect signals
        self.generator_tab.template_path.textChanged.connect(self.color_mapping_tab.refresh_colors)
        self.generator_tab.data_path.textChanged.connect(self.color_mapping_tab.refresh_colors)

        self.statusBar().showMessage("Ready")

    def get_current_config(self):
        config = {
            'template_file': relative_to_app(self.generator_tab.template_path.text()),
            'data_file': relative_to_app(self.generator_tab.data_path.text()),
            'foto_base_dir': relative_to_app(self.generator_tab.photo_dir.text()),
            'foto_subfolder_kelas': self.generator_tab.foto_subfolder.isChecked(),
            'output_svg_dir': relative_to_app(self.output_tab.svg_dir.text()),
            'output_image_dir': relative_to_app(self.output_tab.image_dir.text()),
            'output_formats': self.output_tab.get_output_formats(),
            'include_svg': self.output_tab.chk_svg.isChecked(),
            'image_quality': self.output_tab.jpg_quality.value(),
            'image_dpi': self.output_tab.image_dpi.value(),
            'inkscape_path': self.output_tab.inkscape_path.text(),
            'field_mappings': self.field_config_tab.get_field_mappings(),
            'color_mappings': self.color_mapping_tab.get_color_mappings()
        }
        return config

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except:
                self.config = {}
        else:
            # First run: detect inkscape and set some defaults
            self.config = {
                'inkscape_path': find_inkscape(),
                'output_svg_dir': 'output/svg',
                'output_image_dir': 'output/images'
            }
            if self.config['inkscape_path'] == 'inkscape':
                QTimer.singleShot(500, lambda: QMessageBox.warning(
                    self, "Inkscape Warning", 
                    "Inkscape was not found automatically.\n"
                    "Please set the Inkscape path in Output Settings to enable PNG/PDF export."
                ))

        # Apply to tabs
        self.generator_tab.load_config(self.config)
        self.output_tab.load_config(self.config)
        self.field_config_tab.load_fields(self.config)
        self.color_mapping_tab.load_config(self.config)

    def save_config(self):
        config = self.get_current_config()
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self, "Success", "Configuration saved!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save configuration: {e}")

    def load_config_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON (*.json)")
        if filename:
            with open(filename, 'r') as f:
                self.config = json.load(f)
            self.load_config()
            QMessageBox.information(self, "Success", "Configuration loaded!")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    app.setStyleSheet("""
        QMainWindow { background-color: #2d2d2d; }
        QGroupBox { color: #4ec9b0; font-weight: bold; border: 1px solid #3c3c3c;
                    border-radius: 5px; margin-top: 10px; padding-top: 10px; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        QLabel, QCheckBox { color: #d4d4d4; }
        QLineEdit, QComboBox, QSpinBox {
            background-color: #3c3c3c; color: #d4d4d4; border: 1px solid #555;
            border-radius: 3px; padding: 5px;
        }
        QPushButton {
            background-color: #0e639c; color: white; border: none;
            border-radius: 3px; padding: 8px 15px; font-weight: bold;
        }
        QPushButton:hover { background-color: #1177bb; }
        QPushButton:disabled { background-color: #555; color: #888; }
        QProgressBar { border: 1px solid #3c3c3c; border-radius: 3px; text-align: center; color: #d4d4d4; }
        QProgressBar::chunk { background-color: #0e639c; border-radius: 2px; }
        QTabWidget::pane { border: 1px solid #3c3c3c; background-color: #2d2d2d; }
        QTabBar::tab { background-color: #3c3c3c; color: #d4d4d4; padding: 8px 15px; margin-right: 2px; }
        QTabBar::tab:selected { background-color: #0e639c; color: white; }
        QTableWidget { background-color: #252526; color: #d4d4d4; gridline-color: #3c3c3c; }
        QScrollArea { border: none; }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()