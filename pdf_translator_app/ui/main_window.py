import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QComboBox, QLineEdit, QFileDialog, 
    QListWidget, QProgressBar, QMessageBox, QGroupBox, QFormLayout,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSettings, QSize
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QIcon, QFont, QColor, QAction, QKeySequence

from pdf_translator_app.core.translator import PDFTranslator

# Modern Stylesheet
STYLESHEET = """
QMainWindow {
    background-color: #ffffff;
}
QLabel {
    color: #333333;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}
QGroupBox {
    border: none;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #888888;
    font-weight: bold;
}
QLineEdit, QComboBox {
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 8px 12px;
    background-color: #f8f9fa;
    color: #333;
    selection-background-color: #e0e0e0;
    min-width: 120px; /* Ensure enough width for text */
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #d0d0d0;
    background-color: #ffffff;
}
/* Fix for QComboBox dropdown style */
QComboBox QAbstractItemView {
    border: 1px solid #e0e0e0;
    background-color: #ffffff;
    color: #333333;
    selection-background-color: #f0f0f0;
    selection-color: #333333;
    outline: none;
    padding: 4px;
    min-width: 140px; /* Make dropdown wider than the box if needed */
}
QComboBox QAbstractItemView::item {
    height: 30px;
    padding-left: 10px;  /* Ensure text is aligned to the left with some spacing */
    padding-right: 10px;
    color: #333333;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #e6e6e6;
    color: #000000;
    border: none; /* Remove border to prevent shift */
}
QComboBox QAbstractItemView::item:hover {
    background-color: #f0f0f0;
    color: #000000;
}
QListWidget {
    border: 1px solid #eee;
    border-radius: 8px;
    background-color: #fcfcfc;
    padding: 5px;
}
QPushButton {
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
}
QPushButton#PrimaryButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff00ff, stop:1 #aa00ff);
    color: white;
    border: none;
}
QPushButton#PrimaryButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff33ff, stop:1 #bb33ff);
}
QPushButton#SecondaryButton {
    background-color: #f0f0f0;
    color: #555;
    border: none;
}
QPushButton#SecondaryButton:hover {
    background-color: #e0e0e0;
}
"""

class TranslatorWorker(QThread):
    progress_updated = pyqtSignal(str, int)
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def __init__(self, translator, files, service, lang_in, lang_out, api_key, base_url):
        super().__init__()
        self.translator = translator
        self.files = files
        self.service = service
        self.lang_in = lang_in
        self.lang_out = lang_out
        self.api_key = api_key
        self.base_url = base_url

    def run(self):
        try:
            self.translator.translate_files(
                self.files,
                service=self.service,
                lang_in=self.lang_in,
                lang_out=self.lang_out,
                api_key=self.api_key,
                base_url=self.base_url,
                progress_callback=self.emit_progress
            )
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

    def emit_progress(self, message, percent):
        self.progress_updated.emit(message, percent)

class DropArea(QLabel):
    file_dropped = pyqtSignal(list)

    def __init__(self):
        super().__init__("Drop PDF files here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #e0e0e0;
                border-radius: 16px;
                padding: 40px;
                background-color: #fafafa;
                color: #888;
                font-size: 18px;
                font-weight: 500;
            }
            QLabel:hover {
                border-color: #ff00ff;
                background-color: #fff0ff;
                color: #aa00ff;
            }
        """)
        self.setAcceptDrops(True)
        self.setMinimumHeight(150)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                files.append(file_path)
        if files:
            self.file_dropped.emit(files)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Translator")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(STYLESHEET)
        
        self.settings = QSettings("MyCompany", "PDFTranslatorApp")
        self.translator = PDFTranslator()
        self.files_to_translate = []

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("PDF Translator")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #222;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Main Content - Split into Left (Drop) and Right (Settings)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)

        # Left Column: File Management
        left_layout = QVBoxLayout()
        
        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.add_files)
        left_layout.addWidget(self.drop_area)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #eee;
                border-radius: 8px;
                background-color: #fcfcfc;
                padding: 5px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
                color: #444;
            }
            QListWidget::item:selected {
                background-color: #e0e0e0;
                color: #000;
            }
        """)
        
        # Add delete action for selected items
        self.delete_action = QAction("Delete", self)
        self.delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        self.delete_action.triggered.connect(self.delete_selected_files)
        self.file_list.addAction(self.delete_action)
        
        left_layout.addWidget(self.file_list)

        file_actions = QHBoxLayout()
        self.btn_add = QPushButton("Select Files")
        self.btn_add.setObjectName("SecondaryButton")
        self.btn_add.clicked.connect(self.select_files)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setObjectName("SecondaryButton")
        self.btn_delete.clicked.connect(self.delete_selected_files)
        
        self.btn_clear = QPushButton("Clear All")
        self.btn_clear.setObjectName("SecondaryButton")
        self.btn_clear.clicked.connect(self.clear_files)
        
        file_actions.addWidget(self.btn_add)
        file_actions.addWidget(self.btn_delete)
        file_actions.addWidget(self.btn_clear)
        file_actions.addStretch()
        left_layout.addLayout(file_actions)
        
        content_layout.addLayout(left_layout, stretch=2)

        # Right Column: Settings
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 10, 0, 0)
        
        settings_label = QLabel("Settings")
        settings_label.setStyleSheet("font-size: 16px; font-weight: 600; margin-bottom: 10px;")
        right_layout.addWidget(settings_label)

        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)

        self.service_combo = QComboBox()
        self.service_combo.addItems(["google", "deepl", "openai"])
        self.align_combo_items(self.service_combo)
        self.service_combo.currentTextChanged.connect(self.update_api_fields)
        form_layout.addRow(QLabel("Service"), self.service_combo)

        self.lang_in_combo = QComboBox()
        self.lang_in_combo.addItems(["en", "zh-CN", "ja", "ko", "fr", "de", "es", "ru", "pt", "it", "auto"])
        self.align_combo_items(self.lang_in_combo)
        form_layout.addRow(QLabel("Source Lang"), self.lang_in_combo)

        self.lang_out_combo = QComboBox()
        self.lang_out_combo.addItems(["zh-CN", "en", "ja", "ko", "fr", "de", "es", "ru", "pt", "it"])
        self.align_combo_items(self.lang_out_combo)
        form_layout.addRow(QLabel("Target Lang"), self.lang_out_combo)

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Required for DeepL/OpenAI")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(QLabel("API Key"), self.api_key_input)
        
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("Optional (e.g. OpenAI Proxy)")
        form_layout.addRow(QLabel("Base URL"), self.base_url_input)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()
        
        content_layout.addLayout(right_layout, stretch=1)
        main_layout.addLayout(content_layout)

        # Footer Action Area
        action_layout = QVBoxLayout()
        action_layout.setSpacing(10)
        
        self.status_label = QLabel("Ready to translate")
        self.status_label.setStyleSheet("color: #666; font-size: 13px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        action_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #f0f0f0;
                border-radius: 12px;
                height: 24px;
                text-align: center;
                color: #555;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #ff00ff;
                border-radius: 12px;
            }
        """)
        action_layout.addWidget(self.progress_bar)

        self.btn_translate = QPushButton("Start Translation")
        self.btn_translate.setObjectName("PrimaryButton")
        self.btn_translate.setMinimumHeight(50)
        self.btn_translate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_translate.setStyleSheet("""
            QPushButton#PrimaryButton {
                font-size: 16px;
                border-radius: 25px;
            }
        """)
        self.btn_translate.clicked.connect(self.start_translation)
        action_layout.addWidget(self.btn_translate)

        main_layout.addLayout(action_layout)

    def update_api_fields(self, service):
        is_api_required = service in ["deepl", "openai"]
        self.api_key_input.setEnabled(is_api_required)
        self.base_url_input.setEnabled(service == "openai")
        if not is_api_required:
            self.api_key_input.clear()
            self.base_url_input.clear()

    def align_combo_items(self, combo):
        for i in range(combo.count()):
            combo.setItemData(i, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, Qt.ItemDataRole.TextAlignmentRole)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            self.add_files(files)

    def add_files(self, files):
        for f in files:
            if f not in self.files_to_translate:
                self.files_to_translate.append(f)
                self.file_list.addItem(os.path.basename(f))
        self.status_label.setText(f"{len(self.files_to_translate)} files ready")

    def delete_selected_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            # If no item is selected, try to remove the current item
            current_item = self.file_list.currentItem()
            if current_item:
                selected_items = [current_item]
            else:
                QMessageBox.warning(self, "No Selection", "Please select files to delete.")
                return
            
        # Get indices of selected items
        rows = []
        for item in selected_items:
            rows.append(self.file_list.row(item))
            
        # Sort indices in reverse order to avoid shifting issues when deleting
        rows.sort(reverse=True)
        
        for row in rows:
            if 0 <= row < len(self.files_to_translate):
                del self.files_to_translate[row]
                self.file_list.takeItem(row)
                
        self.status_label.setText(f"{len(self.files_to_translate)} files ready")

    def clear_files(self):
        self.files_to_translate.clear()
        self.file_list.clear()
        self.status_label.setText("Ready to translate")

    def start_translation(self):
        if not self.files_to_translate:
            QMessageBox.warning(self, "No Files", "Please add PDF files to translate.")
            return

        service = self.service_combo.currentText()
        lang_in = self.lang_in_combo.currentText()
        lang_out = self.lang_out_combo.currentText()
        api_key = self.api_key_input.text().strip()
        base_url = self.base_url_input.text().strip()

        if service in ["deepl", "openai"] and not api_key:
            QMessageBox.warning(self, "API Key Missing", f"Please enter an API Key for {service}.")
            return
        
        # Save settings
        self.save_settings()

        # Disable UI
        self.set_ui_enabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing translation...")

        # Start Worker
        self.worker = TranslatorWorker(self.translator, self.files_to_translate, service, lang_in, lang_out, api_key, base_url)
        self.worker.progress_updated.connect(self.update_status)
        self.worker.finished_signal.connect(self.translation_finished)
        self.worker.error_signal.connect(self.translation_error)
        self.worker.start()

    def update_status(self, message, percent):
        self.status_label.setText(message)
        self.progress_bar.setValue(percent)

    def translation_finished(self):
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(100)
        
        # Open output folder directly without showing a popup
        output_dir = os.path.abspath(self.translator.output_dir)
        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':
            os.system(f'open "{output_dir}"')
        else:
            os.system(f'xdg-open "{output_dir}"')
            
        self.status_label.setText("All translations completed successfully")

    def translation_error(self, error_msg):
        self.set_ui_enabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{error_msg}")
        self.status_label.setText("Error occurred during translation")

    def set_ui_enabled(self, enabled):
        self.drop_area.setEnabled(enabled)
        self.btn_add.setEnabled(enabled)
        self.btn_clear.setEnabled(enabled)
        self.btn_translate.setEnabled(enabled)
        self.service_combo.setEnabled(enabled)
        self.api_key_input.setEnabled(enabled)

    def load_settings(self):
        service = self.settings.value("service", "google")
        api_key = self.settings.value("api_key", "")
        base_url = self.settings.value("base_url", "")
        
        index = self.service_combo.findText(service)
        if index >= 0:
            self.service_combo.setCurrentIndex(index)
        
        self.api_key_input.setText(api_key)
        self.base_url_input.setText(base_url)
        self.update_api_fields(service)

    def save_settings(self):
        self.settings.setValue("service", self.service_combo.currentText())
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("base_url", self.base_url_input.text())
