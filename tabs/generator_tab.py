# tabs/generator_tab.py
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pandas as pd
import os

from core.generate_thread import GenerateThread


class GeneratorTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.gen_thread = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # File selection
        file_group = QGroupBox("📁 File Selection")
        file_layout = QFormLayout(file_group)

        self.template_path = QLineEdit('')
        btn_template = QPushButton("Browse")
        btn_template.clicked.connect(lambda: self.browse_file(self.template_path, "SVG (*.svg)"))
        template_layout = QHBoxLayout()
        template_layout.addWidget(self.template_path)
        template_layout.addWidget(btn_template)
        file_layout.addRow("Template SVG:", template_layout)

        self.data_path = QLineEdit('')
        btn_data = QPushButton("Browse")
        btn_data.clicked.connect(lambda: self.browse_file(self.data_path, "Excel (*.xlsx *.xls)"))
        data_layout = QHBoxLayout()
        data_layout.addWidget(self.data_path)
        data_layout.addWidget(btn_data)
        file_layout.addRow("Data Excel:", data_layout)

        self.photo_dir = QLineEdit('')
        btn_photo = QPushButton("Browse")
        btn_photo.clicked.connect(lambda: self.browse_dir(self.photo_dir))
        photo_layout = QHBoxLayout()
        photo_layout.addWidget(self.photo_dir)
        photo_layout.addWidget(btn_photo)
        file_layout.addRow("Photo Directory:", photo_layout)

        self.foto_subfolder = QCheckBox("Search photos in class subfolder (kelas)")
        file_layout.addRow("", self.foto_subfolder)

        left_layout.addWidget(file_group)

        # Preview
        preview_group = QGroupBox("📊 Data Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(300)
        preview_layout.addWidget(self.preview_table)

        btn_refresh = QPushButton("Refresh Preview")
        btn_refresh.clicked.connect(self.refresh_preview)
        preview_layout.addWidget(btn_refresh)

        left_layout.addWidget(preview_group)

        # Progress
        progress_group = QGroupBox("📈 Progress")
        progress_layout = QVBoxLayout(progress_group)

        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready to generate")
        progress_layout.addWidget(self.status_label)

        self.success_label = QLabel("✅ Success: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        self.time_label = QLabel("⏱️ Time: 0s")
        progress_layout.addWidget(self.success_label)
        progress_layout.addWidget(self.failed_label)
        progress_layout.addWidget(self.time_label)

        left_layout.addWidget(progress_group)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)  # Jarak antar tombol
        
        # Tombol START - warna hijau/biru
        self.btn_generate = QPushButton("▶️ Start Generate")
        self.btn_generate.clicked.connect(self.start_generate)
        self.btn_generate.setMinimumHeight(40)
        self.btn_generate.setMinimumWidth(150)  # Ukuran minimal sama
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0a4f7a;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        btn_layout.addWidget(self.btn_generate)
        
        # Tombol STOP - warna merah, ukuran sama
        self.btn_stop = QPushButton("⏹️ Stop")
        self.btn_stop.clicked.connect(self.stop_generate)
        self.btn_stop.setEnabled(False)
        self.btn_stop.setMinimumHeight(40)
        self.btn_stop.setMinimumWidth(150)  # Ukuran minimal sama dengan Start
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #c42b1c;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #e34d3d;
            }
            QPushButton:pressed {
                background-color: #a02010;
            }
            QPushButton:disabled {
                background-color: #5a2a2a;
                color: #888;
            }
        """)
        btn_layout.addWidget(self.btn_stop)
        
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()

        # Right panel - Log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        log_group = QGroupBox("📝 Log Output")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)

        btn_clear = QPushButton("Clear Log")
        btn_clear.clicked.connect(self.log_text.clear)
        log_layout.addWidget(btn_clear)

        right_layout.addWidget(log_group)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([600, 600])

    def browse_file(self, line_edit, file_filter):
        filename, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if filename:
            line_edit.setText(filename)

    def browse_dir(self, line_edit):
        dirname = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dirname:
            line_edit.setText(dirname)

    def refresh_preview(self):
        try:
            from core.paths import resolve_path
            data_file = resolve_path(self.data_path.text())
            if not os.path.exists(data_file):
                self.log_text.append(f"⚠️ File not found: {data_file}")
                return

            df = pd.read_excel(data_file)
            self.preview_table.setRowCount(min(50, len(df)))
            self.preview_table.setColumnCount(len(df.columns))
            self.preview_table.setHorizontalHeaderLabels(df.columns.tolist())

            for i in range(min(50, len(df))):
                for j in range(len(df.columns)):
                    value = df.iloc[i, j]
                    self.preview_table.setItem(i, j, QTableWidgetItem(str(value)))

            self.parent.statusBar().showMessage(f"Preview loaded: {len(df)} rows")
        except Exception as e:
            self.log_text.append(f"❌ Error loading preview: {e}")

    def start_generate(self, config=None):
        if config is None or not isinstance(config, dict):
            config = self.parent.get_current_config()

        print("CONFIG TYPE:", type(config))
        print("CONFIG:", config)

        self.progress_bar.setValue(0)
        self.success_label.setText("✅ Success: 0")
        self.failed_label.setText("❌ Failed: 0")
        self.time_label.setText("⏱️ Time: 0s")
        self.log_text.clear()

        self.btn_generate.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.gen_thread = GenerateThread(config)
        self.gen_thread.progress.connect(self.update_progress)
        self.gen_thread.log.connect(self.log_text.append)
        self.gen_thread.finished.connect(self.on_generate_finished)
        self.gen_thread.start()

    def stop_generate(self):
        if self.gen_thread and self.gen_thread.isRunning():
            self.gen_thread.stop()
            self.log_text.append("⚠️ Stopping generation...")

    def update_progress(self, current, total, status):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(status)

    def on_generate_finished(self, stats):
        self.btn_generate.setEnabled(True)
        self.btn_stop.setEnabled(False)

        self.success_label.setText(f"✅ Success: {stats.get('success', 0)}")
        self.failed_label.setText(f"❌ Failed: {stats.get('failed', 0)}")
        self.time_label.setText(f"⏱️ Time: {stats.get('time', 0)}s")

        self.log_text.append("\n" + "="*50)
        self.log_text.append(f"✨ GENERATION COMPLETE ✨")
        self.log_text.append(f"✅ Success: {stats.get('success', 0)}")
        self.log_text.append(f"❌ Failed: {stats.get('failed', 0)}")
        self.log_text.append(f"⏱️ Time: {stats.get('time', 0)} seconds")

        if stats.get('errors'):
            self.log_text.append(f"\n📋 Errors:")
            for error in stats['errors'][:10]:
                self.log_text.append(f"  • {error}")

        QMessageBox.information(self, "Complete",
            f"Generation Complete!\n\n"
            f"✅ Success: {stats.get('success', 0)}\n"
            f"❌ Failed: {stats.get('failed', 0)}\n"
            f"⏱️ Time: {stats.get('time', 0)} seconds")

    def load_config(self, config):
        from core.paths import resolve_path
        self.template_path.setText(resolve_path(config.get('template_file', '')))
        self.data_path.setText(resolve_path(config.get('data_file', '')))
        self.photo_dir.setText(resolve_path(config.get('foto_base_dir', '')))
        self.foto_subfolder.setChecked(config.get('foto_subfolder_kelas', False))