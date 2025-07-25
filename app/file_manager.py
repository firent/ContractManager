import os
import shutil
from datetime import datetime
from pathlib import Path


def ensure_documents_dir():
    """Создает папку для документов, если ее нет"""
    docs_dir = Path('data/documents')
    docs_dir.mkdir(parents=True, exist_ok=True)
    return docs_dir

def save_document(file_obj, contract_number):
    """Сохраняет PDF-документ в папку documents"""
    docs_dir = ensure_documents_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"contract_{contract_number}_{timestamp}.pdf"
    file_path = docs_dir / file_name
    
    with open(file_path, 'wb') as f:
        shutil.copyfileobj(file_obj, f)
    
    return file_name, str(file_path)

def delete_document(file_path):
    """Удаляет документ"""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False
