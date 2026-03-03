import sys
import os
from PyQt6.QtWidgets import QApplication

# Ensure the project root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Qt plugin path if needed (especially for conda/venv environments)
import site
for p in site.getsitepackages():
    qt_plugin_path = os.path.join(p, "PyQt6", "Qt6", "plugins")
    if os.path.exists(qt_plugin_path):
        os.environ["QT_PLUGIN_PATH"] = qt_plugin_path
        break

from pdf_translator_app.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
