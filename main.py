from PyQt5.QtWidgets import *
import sys
from recover import Recover
import signatures
from sup import get_disks
from PyQt5.QtWidgets import QFileDialog


class RecoveryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("File Recovery App")
        self.setGeometry(200, 200, 400, 600)

        # Layouts
        main_layout = QVBoxLayout()
        file_system_layout = QHBoxLayout()
        disks_layout = QVBoxLayout()
        recovery_path_layout = QHBoxLayout()
        file_types_layout = QVBoxLayout()
        start_layout = QVBoxLayout()

        # File system selection
        file_system_label = QLabel("Файловая система:")
        self.file_system_combo = QComboBox()
        self.file_system_combo.addItems(["NTFS", "FAT"])
        file_system_layout.addWidget(file_system_label)
        file_system_layout.addWidget(self.file_system_combo)

        # Disk selection
        disks_label = QLabel("Что восстанавливаем:")
        self.disks_list = QListWidget()
        print(get_disks())
        self.disks_list.addItems(get_disks())
        self.disks_list.itemSelectionChanged.connect(self.update_start_button)  # Update when selection changes
        disks_layout.addWidget(disks_label)
        disks_layout.addWidget(self.disks_list)

        # Recovery path
        recovery_path_label = QLabel("Куда восстановить:")
        self.recovery_path_input = QLineEdit()

        # Добавляем кнопку для выбора директории
        self.select_folder_button = QPushButton("Выбрать папку")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.recovery_path_input.textChanged.connect(self.update_start_button)  # Update when text changes
        recovery_path_layout.addWidget(self.select_folder_button)
        recovery_path_layout.addWidget(self.recovery_path_input)

        # File types
        file_types_label = QLabel("Какие файлы восстанавливаем:")
        file_types_layout.addWidget(file_types_label)
        self.file_types_checkboxes = []
        for file_type in [f'.{i}' for i in signatures.file_signatures]:
            checkbox = QCheckBox(file_type)
            checkbox.stateChanged.connect(self.update_start_button)  # Update when checkbox state changes
            self.file_types_checkboxes.append(checkbox)
            file_types_layout.addWidget(checkbox)

        # Start button and progress bar
        self.start_button = QPushButton("Старт")
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("0.00%")
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        # Initially disable the start button
        self.start_button.setEnabled(False)

        start_layout.addWidget(self.start_button)
        start_layout.addWidget(self.progress_bar)
        start_layout.addWidget(self.progress_label)
        start_layout.addWidget(self.log_text)

        # Adding all layouts to the main layout
        main_layout.addLayout(file_system_layout)
        main_layout.addLayout(disks_layout)
        main_layout.addLayout(recovery_path_layout)
        main_layout.addLayout(file_types_layout)
        main_layout.addLayout(start_layout)

        # Setting the main layout
        self.setLayout(main_layout)

        # Connect signals
        self.start_button.clicked.connect(self.start_recovery)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите директорию для восстановления")
        if folder:
            self.recovery_path_input.setText(folder)

    def update_start_button(self):
        # Проверяем, выбраны ли диск, путь для восстановления и хотя бы один тип файла
        disk_selected = bool(self.disks_list.selectedItems())
        recovery_path_filled = bool(self.recovery_path_input.text())
        file_types_selected = any(checkbox.isChecked() for checkbox in self.file_types_checkboxes)

        if disk_selected and recovery_path_filled and file_types_selected:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)

    def start_recovery(self):
        # Пример работы с восстановлением
        selected_disk = self.disks_list.selectedItems()[0].text()  # Получаем выбранный диск
        rec = Recover(fr'\\.\{selected_disk}', self.recovery_path_input.text())
        rec.scan_signatures(self.progress_bar, self.progress_label, self.log_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RecoveryApp()
    window.show()
    sys.exit(app.exec_())