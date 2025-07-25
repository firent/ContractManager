import os
from datetime import date
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableView, QHeaderView, 
    QPushButton, QHBoxLayout, QMessageBox, QInputDialog, QLabel,
    QMenu
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from ..database import get_session
from ..models import Contract
from ..notifications import check_expiring_contracts
from .table_model import ContractsTableModel
from .contract_form import ContractForm
from .excel_utils import export_to_excel, import_from_excel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление договорами 1.0")
        self.resize(1200, 700)
        
        self.session = get_session()
        self.setup_ui()
        self.setup_menu()
        self.load_contracts()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_contract)
        
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.clicked.connect(self.edit_contract)
        
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_contract)
        
        self.search_button = QPushButton("Поиск")
        self.search_button.clicked.connect(self.search_contracts)
        
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_contracts)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.search_button)
        button_layout.addWidget(self.refresh_button)
        
        # Таблица договоров
        self.table = QTableView()
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self.edit_contract)
        
        # Включение контекстного меню
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        # Статус бар
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        layout.addWidget(self.status_label)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
    
    def setup_menu(self):
        """Настройка меню"""
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu("Файл")
        
        export_action = QAction("Экспорт в Excel", self)
        export_action.triggered.connect(self.export_excel)
        file_menu.addAction(export_action)
        
        import_action = QAction("Импорт из Excel", self)
        import_action.triggered.connect(self.import_excel)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Действия
        action_menu = menubar.addMenu("Действия")
        
        check_expiring_action = QAction("Проверить истекающие", self)
        check_expiring_action.triggered.connect(self.check_expiring)
        action_menu.addAction(check_expiring_action)
        
        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        license_action = QAction("Лицензия", self)
        license_action.triggered.connect(self.show_license)
        help_menu.addAction(license_action)
    
    def show_about(self):
        """Показывает информацию о программе"""
        about_text = """<b>Управление договорами</b><br><br>
        Версия 1.0<br>
        Программа для учета и управления договорами<br><br>
        © 2025 Иван Пожидаев. Все права защищены."""
        QMessageBox.about(self, "О программе", about_text)
    
    def show_license(self):
        """Показывает лицензионное соглашение"""
        license_text = """<b>Лицензия MIT</b><br><br>
        Copyright (c) 2025 Иван Пожидаев<br>
        E-mail: ivan@ivanpozhidaev.ru<br><br>
        Эта программа распространяется под лицензией MIT. Разрешается использование, копирование
        и распространение этой программы в любых целях, при условии указания авторства. <br>"""
        QMessageBox.information(self, "Лицензия", license_text)
    
    def show_context_menu(self, position):
        """Показывает контекстное меню для таблицы"""
        menu = QMenu()
        
        export_action = QAction("Экспорт выделенного", self)
        export_action.triggered.connect(self.export_selected)
        menu.addAction(export_action)
        
        view_doc_action = QAction("Просмотреть документ", self)
        view_doc_action.triggered.connect(self.view_document)
        menu.addAction(view_doc_action)
        
        menu.exec(self.table.viewport().mapToGlobal(position))
    
    def load_contracts(self):
        """Загрузка договоров в таблицу"""
        contracts = self.session.query(Contract).order_by(Contract.end_date).all()
        
        headers = ["Номер", "Наименование", "Контрагент", "Начало", "Окончание", "Осталось"]
        self.model = ContractsTableModel(contracts, headers)
        self.table.setModel(self.model)
        
        # Обновление статус бара
        today = date.today()
        active = sum(1 for c in contracts if c.end_date >= today)
        expired = len(contracts) - active
        self.status_label.setText(
            f"Всего договоров: {len(contracts)} | Активных: {active} | Истекших: {expired}")
    
    def export_excel(self):
        """Экспорт всех договоров в Excel"""
        contracts = self.session.query(Contract).all()
        if not contracts:
            QMessageBox.warning(self, "Внимание", "Нет договоров для экспорта!")
            return
        
        success, message = export_to_excel(contracts, self)
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def export_selected(self):
        """Экспорт выбранных договоров в Excel"""
        contracts = self.get_selected_contracts()
        if not contracts:
            QMessageBox.warning(self, "Внимание", "Выберите договоры для экспорта!")
            return
        
        success, message = export_to_excel(contracts, self)
        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def import_excel(self):
        """Импорт договоров из Excel"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите импортировать договоры из Excel?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = import_from_excel(self.session, self)
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_contracts()
            else:
                QMessageBox.warning(self, "Ошибка", message)
    
    def get_selected_contracts(self):
        """Возвращает список выбранных договоров"""
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return []
        
        return [self.model._data[index.row()] for index in indexes]
    
    def add_contract(self):
        """Добавление нового договора"""
        form = ContractForm()
        if form.exec():
            data = form.get_data()
        
            try:
                contract = Contract(
                    number=data['number'],
                    name=data['name'],
                    counterparty=data['counterparty'],
                    start_date=data['start_date'],
                    end_date=data['end_date'],
                    description=data['description']
                )
            
                self.session.add(contract)
                self.session.commit()  # Сначала сохраняем договор, чтобы получить ID
            
                # Прикрепление документа, если есть
                if data['file_path']:
                    self.attach_document(contract, data['file_path'])
                    self.session.commit()  # Сохраняем документ
            
                self.load_contracts()
                QMessageBox.information(self, "Успех", "Договор успешно добавлен!")
        
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить договор: {str(e)}")
    
    def edit_contract(self):
        """Редактирование договора"""
        contract = self.get_selected_contract()
        if not contract:
            return
    
        form = ContractForm(contract)
        if form.exec():
            data = form.get_data()
        
            try:
                contract.number = data['number']
                contract.name = data['name']
                contract.counterparty = data['counterparty']
                contract.start_date = data['start_date']
                contract.end_date = data['end_date']
                contract.description = data['description']
            
                # Проверяем, был ли выбран новый файл
                if data['file_path']:
                    # Если у договора уже есть документ
                    if contract.documents:
                        current_file = contract.documents[0].file_path
                        # Если выбран другой файл
                        if data['file_path'] != current_file:
                            from ..file_manager import delete_document
                            delete_document(current_file)
                            self.session.delete(contract.documents[0])
                            self.attach_document(contract, data['file_path'])
                    else:
                        # Если документа не было, просто прикрепляем новый
                        self.attach_document(contract, data['file_path'])
            
                self.session.commit()
                self.load_contracts()
                QMessageBox.information(self, "Успех", "Договор успешно обновлен!")
        
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить договор: {str(e)}")
    
    def delete_contract(self):
        """Удаление договора"""
        contract = self.get_selected_contract()
        if not contract:
            return
        
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Вы уверены, что хотите удалить договор {contract.number}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удаление связанных документов
                if contract.documents:
                    from ..file_manager import delete_document
                    delete_document(contract.documents[0].file_path)
                
                self.session.delete(contract)
                self.session.commit()
                self.load_contracts()
                QMessageBox.information(self, "Успех", "Договор успешно удален!")
            
            except Exception as e:
                self.session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить договор: {str(e)}")
    
    def get_selected_contract(self):
        """Возвращает выбранный в таблице договор"""
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Внимание", "Выберите договор из таблицы!")
            return None
        
        return self.model._data[indexes[0].row()]
    
    def search_contracts(self):
        """Поиск договоров"""
        text, ok = QInputDialog.getText(
            self, "Поиск договоров", "Введите номер, название или контрагента:")
        
        if ok and text:
            contracts = self.session.query(Contract).filter(
                (Contract.number.ilike(f"%{text}%")) |
                (Contract.name.ilike(f"%{text}%")) |
                (Contract.counterparty.ilike(f"%{text}%"))
            ).order_by(Contract.end_date).all()
            
            self.load_contracts(contracts)
    
    def attach_document(self, contract, file_path):
        """Прикрепление документа к договору"""
        from ..file_manager import save_document
        from ..models import Document
        
        try:
            with open(file_path, 'rb') as file_obj:
                file_name, saved_path = save_document(file_obj, contract.number)
                
                document = Document(
                    contract_id=contract.id,
                    file_name=file_name,
                    file_path=saved_path
                )
                
                self.session.add(document)
                self.session.commit()
        
        except Exception as e:
            raise Exception(f"Ошибка при загрузке файла: {str(e)}")
    
    def view_document(self):
        """Просмотр прикрепленного документа"""
        contract = self.get_selected_contract()
        if not contract:
            return
        
        if not contract.documents:
            QMessageBox.information(self, "Информация", "Нет прикрепленных документов")
            return
        
        try:
            os.startfile(contract.documents[0].file_path)
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {str(e)}")
    
    def check_expiring(self):
        """Проверка истекающих договоров"""
        expiring = check_expiring_contracts(self.session)
        if expiring:
            msg = "Следующие договоры скоро истекают:\n\n"
            msg += "\n".join(
                f"- {c.number} ({c.counterparty}): {c.end_date.strftime('%d.%m.%Y')} "
                f"(осталось {(c.end_date - date.today()).days} дней)"
                for c in expiring
            )
            
            QMessageBox.warning(self, "Внимание", msg)
        else:
            QMessageBox.information(self, "Информация", "Нет договоров, которые скоро истекают")
    
    def closeEvent(self, event):
        """Закрытие приложения"""
        self.session.close()
        event.accept()
        