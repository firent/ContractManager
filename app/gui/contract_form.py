from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QTextEdit, 
    QDialogButtonBox, QFileDialog, QLabel, QPushButton, QHBoxLayout
)
from PySide6.QtCore import QDate, QUrl
from PySide6.QtGui import QDesktopServices
from pathlib import Path

class ContractForm(QDialog):
    def __init__(self, contract=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать договор" if contract else "Новый договор")
        self.setMinimumWidth(500)
        
        self.contract = contract
        self.file_path = None
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        # Поля формы
        self.number_edit = QLineEdit()
        self.name_edit = QLineEdit()
        self.counterparty_edit = QLineEdit()
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("dd.MM.yyyy")
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("dd.MM.yyyy")
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        
        # Виджеты для работы с файлом
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setWordWrap(True)
        
        # Кнопки для файла
        file_button_layout = QHBoxLayout()
        
        self.file_button = QPushButton("Выбрать PDF")
        self.file_button.clicked.connect(self.select_file)
        
        self.view_file_button = QPushButton("Просмотреть")
        self.view_file_button.clicked.connect(self.view_file)
        self.view_file_button.setEnabled(False)
        
        file_button_layout.addWidget(self.file_button)
        file_button_layout.addWidget(self.view_file_button)
        
        # Добавление полей в форму
        form_layout.addRow("Номер договора:", self.number_edit)
        form_layout.addRow("Наименование:", self.name_edit)
        form_layout.addRow("Контрагент:", self.counterparty_edit)
        form_layout.addRow("Дата начала:", self.start_date_edit)
        form_layout.addRow("Дата окончания:", self.end_date_edit)
        form_layout.addRow("Описание:", self.description_edit)
        form_layout.addRow("Документ:", file_button_layout)
        form_layout.addRow("", self.file_label)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)
        
        # Заполнение формы, если передан договор
        if contract:
            self.fill_form_with_contract_data(contract)
    
    def fill_form_with_contract_data(self, contract):
        """Заполняет форму данными из договора"""
        self.number_edit.setText(contract.number)
        self.name_edit.setText(contract.name)
        self.counterparty_edit.setText(contract.counterparty)
        self.start_date_edit.setDate(QDate(contract.start_date.year, contract.start_date.month, contract.start_date.day))
        self.end_date_edit.setDate(QDate(contract.end_date.year, contract.end_date.month, contract.end_date.day))
        self.description_edit.setText(contract.description or "")
        
        if contract.documents:
            doc = contract.documents[0]
            self.file_label.setText(doc.file_name)
            self.file_path = doc.file_path
            self.view_file_button.setEnabled(True)
    
    def select_file(self):
        """Выбор файла для прикрепления"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "PDF Files (*.pdf)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(Path(file_path).name)
            self.view_file_button.setEnabled(True)
    
    def view_file(self):
        """Просмотр прикрепленного файла"""
        if self.file_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.file_path))
    
    def get_data(self):
        """Возвращает данные из формы"""
        return {
            "number": self.number_edit.text().strip(),
            "name": self.name_edit.text().strip(),
            "counterparty": self.counterparty_edit.text().strip(),
            "start_date": self.start_date_edit.date().toPython(),
            "end_date": self.end_date_edit.date().toPython(),
            "description": self.description_edit.toPlainText().strip() or None,
            "file_path": self.file_path
        }
    