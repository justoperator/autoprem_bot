from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base

BaseUsers = declarative_base()
BaseAdmins = declarative_base()


class User(BaseUsers):
    """ORM model for bot users table."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    reg_date = Column(DateTime, default=datetime.utcnow)
    lang_code = Column(String(2))


class Admin(BaseAdmins):
    """ORM model for bot admins table."""
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    status = Column(String(50))
