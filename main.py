import sys
import os
from PySide6.QtWidgets import QApplication
from app.database import init_db
from app.gui.main_window import MainWindow


def resource_path(relative_path):
    """ Получение абсолютного пути к ресурсам """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    # Установка корректного пути к БД
    os.environ['DB_PATH'] = resource_path('data/contracts.db')
    
    # Инициализация базы данных
    init_db()
    
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Настройка темы
    app.setStyle('Fusion')
    
    # Главное окно
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
