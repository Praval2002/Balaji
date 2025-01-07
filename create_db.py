from sqlalchemy import create_engine, Column, Integer, String, Numeric, Enum, Date, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DB_NAME = 'Bala_test.db'  

DATABASE_URI = f"sqlite:///{DB_NAME}"  

engine = create_engine(DATABASE_URI, echo=True)

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    salary = Column(Numeric(10, 2), nullable=True)
    expenses = Column(Numeric(10, 2), nullable=True)
    role = Column(Enum('user', 'admin'), default='user')
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    expenses_list = relationship('Expense', backref='user')

class Expense(Base):
    __tablename__ = 'expense'

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    expense_date = Column(Date, nullable=False)
    status = Column(Enum('cleared', 'pending'), default='pending')
    amount = Column(Numeric(10, 2), nullable=True)
    expense_image = Column(String(255), nullable=True)

def create_tables():
    Base.metadata.create_all(engine)  
    print("Tables `user` and `expense` created successfully!")

if __name__ == '__main__':
    create_tables()
