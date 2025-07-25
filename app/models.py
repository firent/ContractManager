from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

Base = declarative_base()

class Contract(Base):
    __tablename__ = 'contracts'
    
    id = Column(Integer, primary_key=True)
    number = Column(String(50), nullable=False, unique=True)
    name = Column(String(200), nullable=False)
    counterparty = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    description = Column(Text)
    status = Column(String(20), default='active')
    
    documents = relationship("Document", back_populates="contract")
    
    def days_remaining(self):
        return (self.end_date - date.today()).days
    
    def is_expiring_soon(self, days=30):
        return 0 <= self.days_remaining() <= days

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_date = Column(Date, default=date.today())
    
    contract = relationship("Contract", back_populates="documents")
    