# tabs/output_tab.py
from PyQt6.QtWidgets import *


class OutputTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Output formats
        format_group = QGroupBox("🎨 Output Formats")
        format_layout = QVBoxLayout(format_group)

        self.chk_svg = QCheckBox("Include SVG files (for editing)")
        self.chk_svg.setChecked(True)
        format_layout.addWidget(self.chk_svg)

        self.chk_png = QCheckBox("Generate PNG")
        self.chk_png.setChecked(True)
        format_layout.addWidget(self.chk_png)

        self.chk_jpg = QCheckBox("Generate JPG")
        self.chk_jpg.setChecked(False)
        format_layout.addWidget(self.chk_jpg)

        self.chk_pdf = QCheckBox("Generate PDF")
        self.chk_pdf.setChecked(False)
        format_layout.addWidget(self.chk_pdf)

        layout.addWidget(format_group)

        # Output directories
        dir_group = QGroupBox("📁 Output Directories")
        dir_layout = QFormLayout(dir_group)

        self.svg_dir = QLineEdit('output/svg')
        btn_svg_dir = QPushButton("Browse")
        btn_svg_dir.clicked.connect(lambda: self.browse_dir(self.svg_dir))
        svg_layout = QHBoxLayout()
        svg_layout.addWidget(self.svg_dir)
        svg_layout.addWidget(btn_svg_dir)
        dir_layout.addRow("SVG Output:", svg_layout)

        self.image_dir = QLineEdit('output/images')
        btn_img_dir = QPushButton("Browse")
        btn_img_dir.clicked.connect(lambda: self.browse_dir(self.image_dir))
        img_layout = QHBoxLayout()
        img_layout.addWidget(self.image_dir)
        img_layout.addWidget(btn_img_dir)
        dir_layout.addRow("Image Output:", img_layout)

        layout.addWidget(dir_group)

        # Image settings
        img_group = QGroupBox("🖼️ Image Settings")
        img_layout = QFormLayout(img_group)

        self.image_dpi = QSpinBox()
        self.image_dpi.setRange(72, 600)
        self.image_dpi.setValue(300)
        img_layout.addRow("DPI:", self.image_dpi)

        self.jpg_quality = QSpinBox()
        self.jpg_quality.setRange(1, 100)
        self.jpg_quality.setValue(95)
        img_layout.addRow("JPG Quality (%):", self.jpg_quality)

        layout.addWidget(img_group)

        # External Tools
        tools_group = QGroupBox("⚙️ External Tools")
        tools_layout = QFormLayout(tools_group)

        self.inkscape_path = QLineEdit('inkscape')
        btn_inkscape = QPushButton("Browse")
        btn_inkscape.clicked.connect(self.browse_inkscape)
        inkscape_layout = QHBoxLayout()
        inkscape_layout.addWidget(self.inkscape_path)
        inkscape_layout.addWidget(btn_inkscape)
        tools_layout.addRow("Inkscape Executable:", inkscape_layout)

        layout.addWidget(tools_group)
        layout.addStretch()

    def browse_dir(self, line_edit):
        dirname = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dirname:
            line_edit.setText(dirname)

    def browse_inkscape(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Inkscape Executable", "", "Executable (*.exe);;All Files (*)")
        if filename:
            self.inkscape_path.setText(filename)

    def get_output_formats(self):
        formats = []
        if self.chk_png.isChecked():
            formats.append('png')
        if self.chk_jpg.isChecked():
            formats.append('jpg')
        if self.chk_pdf.isChecked():
            formats.append('pdf')
        return formats

    def load_config(self, config):
        from core.paths import resolve_path
        self.svg_dir.setText(resolve_path(config.get('output_svg_dir', 'output/svg')))
        self.image_dir.setText(resolve_path(config.get('output_image_dir', 'output/images')))
        self.chk_svg.setChecked(config.get('include_svg', True))
        self.chk_png.setChecked('png' in config.get('output_formats', []))
        self.chk_jpg.setChecked('jpg' in config.get('output_formats', []))
        self.chk_pdf.setChecked('pdf' in config.get('output_formats', []))
        self.jpg_quality.setValue(config.get('image_quality', 95))
        self.image_dpi.setValue(config.get('image_dpi', 300))
        self.inkscape_path.setText(resolve_path(config.get('inkscape_path', 'inkscape')))