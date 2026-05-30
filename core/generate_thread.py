# core/generate_thread.py
from PyQt6.QtCore import QThread, pyqtSignal
import traceback
from .generate import FlexibleGenerator


class GenerateThread(QThread):
    progress = pyqtSignal(int, int, str)
    log = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.running = True

    def run(self):
        generator = FlexibleGenerator(self.config)

        def progress_callback(current, total, status):
            if not self.running:
                raise Exception("Stopped by user")
            self.progress.emit(current, total, status)
            self.log.emit(f"[{current}/{total}] {status}")

        try:
            stats = generator.generate_all(progress_callback)
            self.finished.emit(stats)
        except Exception as e:
            tb = traceback.format_exc()

            print(tb)

            self.log.emit(f"❌ Error:\n{tb}")

            self.finished.emit({
                'success': 0,
                'failed': 0,
                'time': 0,
                'errors': [tb]
            })

    def stop(self):
        self.running = False