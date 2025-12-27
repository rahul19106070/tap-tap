from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String)
    first_name = Column(String)
    coins = Column(Float, default=0.0)
    referral_code = Column(String, unique=True)
    referred_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    is_admin = Column(Boolean, default=False)
    level = Column(Integer, default=1)
    total_earned = Column(Float, default=0.0)
    tasks_completed = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    assigned_tasks = relationship('Task', foreign_keys='Task.assigned_to', back_populates='assignee')
    created_tasks = relationship('Task', foreign_keys='Task.created_by', back_populates='creator')
    referrals = relationship('User', remote_side=[id], backref='referrer')
    transactions = relationship('Transaction', back_populates='user')

class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    assigned_to = Column(Integer, ForeignKey('users.id'), nullable=True)
    reward_coins = Column(Float, default=10.0)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = relationship('User', foreign_keys=[created_by], back_populates='created_tasks')
    assignee = relationship('User', foreign_keys=[assigned_to], back_populates='assigned_tasks')

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String, nullable=False)  # 'task_reward', 'referral_bonus', 'task_creation'
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='transactions')

class Database:
    def __init__(self, db_path='bot.db'):
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()
    
    def get_or_create_user(self, telegram_id, username=None, first_name=None):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            if not user:
                import secrets
                referral_code = secrets.token_urlsafe(8)
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    referral_code=referral_code
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                # Update username if changed
                if username and user.username != username:
                    user.username = username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                session.commit()
            return user
        finally:
            session.close()
    
    def get_user_by_referral_code(self, referral_code):
        session = self.get_session()
        try:
            return session.query(User).filter_by(referral_code=referral_code).first()
        finally:
            session.close()
    
    def add_coins(self, user_id, amount, transaction_type, description=None):
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                user.coins += amount
                transaction = Transaction(
                    user_id=user_id,
                    amount=amount,
                    transaction_type=transaction_type,
                    description=description
                )
                session.add(transaction)
                session.commit()
                return user.coins
            return None
        finally:
            session.close()


