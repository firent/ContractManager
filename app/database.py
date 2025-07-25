import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

def init_db(db_path='data/contracts.db'):
    """Инициализация базы данных"""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine

def get_session(engine=None):
    """Создание сессии"""
    if engine is None:
        engine = init_db()
    Session = sessionmaker(bind=engine)
    return Session()

