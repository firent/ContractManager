from datetime import date, timedelta
from .models import Contract

def check_expiring_contracts(session, days=30):
    """Проверяет договоры, которые скоро истекают"""
    today = date.today()
    end_date = today + timedelta(days=days)
    
    expiring_contracts = session.query(Contract).filter(
        Contract.end_date >= today,
        Contract.end_date <= end_date,
        Contract.status == 'active'
    ).all()
    
    return expiring_contracts

def send_notification(contract):
    """Отправляет уведомление о скором окончании договора"""
    days_left = (contract.end_date - date.today()).days
    print(f"\n! ВНИМАНИЕ: Договор {contract.number} '{contract.name}' "
          f"с {contract.counterparty} истекает через {days_left} дней "
          f"(до {contract.end_date.strftime('%d.%m.%Y')})")
    