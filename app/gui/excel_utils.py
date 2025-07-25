import pandas as pd
from datetime import datetime
from PySide6.QtWidgets import QFileDialog
from ..models import Contract

def export_to_excel(contracts, parent=None):
    """Экспорт договоров в Excel"""
    try:
        # Преобразуем данные договоров в словарь
        data = []
        for contract in contracts:
            data.append({
                "Номер": contract.number,
                "Наименование": contract.name,
                "Контрагент": contract.counterparty,
                "Дата начала": contract.start_date.strftime("%d.%m.%Y"),
                "Дата окончания": contract.end_date.strftime("%d.%m.%Y"),
                "Дней осталось": (contract.end_date - datetime.now().date()).days,
                "Статус": "Активен" if contract.end_date >= datetime.now().date() else "Истек",
                "Описание": contract.description or ""
            })
        
        # Создаем DataFrame
        df = pd.DataFrame(data)
        
        # Выбираем файл для сохранения
        file_path, _ = QFileDialog.getSaveFileName(
            parent, "Экспорт в Excel", "", "Excel Files (*.xlsx)")
        
        if file_path:
            # Добавляем расширение, если его нет
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            # Экспортируем в Excel
            df.to_excel(file_path, index=False, sheet_name='Договоры')
            return True, "Экспорт успешно завершен!"
    
    except Exception as e:
        return False, f"Ошибка при экспорте: {str(e)}"
    
    return False, "Экспорт отменен"

def import_from_excel(session, parent=None):
    """Импорт договоров из Excel"""
    try:
        # Выбираем файл для импорта
        file_path, _ = QFileDialog.getOpenFileName(
            parent, "Импорт из Excel", "", "Excel Files (*.xlsx *.xls)")
        
        if not file_path:
            return False, "Импорт отменен"
        
        # Читаем Excel файл
        df = pd.read_excel(file_path)
        
        # Проверяем необходимые колонки
        required_columns = ["Номер", "Наименование", "Контрагент", "Дата начала", "Дата окончания"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            return False, f"Отсутствуют обязательные колонки: {', '.join(missing_cols)}"
        
        # Импортируем данные
        imported = 0
        skipped = 0
        errors = []
        
        for _, row in df.iterrows():
            try:
                # Парсим даты
                from datetime import datetime as dt
                start_date = dt.strptime(str(row["Дата начала"]), "%d.%m.%Y").date()
                end_date = dt.strptime(str(row["Дата окончания"]), "%d.%m.%Y").date()
                
                # Проверяем, существует ли уже договор с таким номером
                existing = session.query(Contract).filter_by(number=str(row["Номер"])).first()
                if existing:
                    skipped += 1
                    continue
                
                # Создаем новый договор
                contract = Contract(
                    number=str(row["Номер"]),
                    name=str(row["Наименование"]),
                    counterparty=str(row["Контрагент"]),
                    start_date=start_date,
                    end_date=end_date,
                    description=str(row["Описание"]) if "Описание" in df.columns else None
                )
                
                session.add(contract)
                imported += 1
            
            except Exception as e:
                errors.append(f"Строка {_ + 2}: {str(e)}")
                continue
        
        session.commit()
        
        message = f"Импорт завершен. Успешно: {imported}, Пропущено: {skipped}"
        if errors:
            message += f"\nОшибки ({len(errors)}):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                message += f"\n...и еще {len(errors) - 5} ошибок"
        
        return True, message
    
    except Exception as e:
        session.rollback()
        return False, f"Ошибка при импорте: {str(e)}"