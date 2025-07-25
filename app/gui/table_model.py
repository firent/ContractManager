from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QColor
from datetime import date

class ContractsTableModel(QAbstractTableModel):
    def __init__(self, data, headers, parent=None):
        super().__init__(parent)
        self._data = data
        self._headers = headers
    
    def rowCount(self, parent=None):
        return len(self._data)
    
    def columnCount(self, parent=None):
        return len(self._headers)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        
        contract = self._data[index.row()]
        col = index.column()
        
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if col == 0:
                return contract.number
            elif col == 1:
                return contract.name
            elif col == 2:
                return contract.counterparty
            elif col == 3:
                return contract.start_date.strftime("%d.%m.%Y")
            elif col == 4:
                return contract.end_date.strftime("%d.%m.%Y")
            elif col == 5:
                days_left = (contract.end_date - date.today()).days
                return f"{days_left} дней" if days_left >= 0 else "Истек"
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            days_left = (contract.end_date - date.today()).days
            if days_left < 0:  # Истекшие
                return QColor('#DC143C')  # Красный
            elif days_left <= 30:  # Скоро истекают
                return QColor('#FFFF00')  # Желтый
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None
    
    def get_contract(self, row):
        """Возвращает договор по номеру строки"""
        if 0 <= row < len(self._data):
            return self._data[row]
        return None
    