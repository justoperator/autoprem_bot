from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.paths import usersDB, adminsDB
from .models import BaseUsers, BaseAdmins

# Engines
engine_users = create_engine(f"sqlite:///{usersDB}", echo=False)
engine_admins = create_engine(f"sqlite:///{adminsDB}", echo=False)

# Sessions
SessionUsers = sessionmaker(bind=engine_users)
SessionAdmins = sessionmaker(bind=engine_admins)

# Create tables
BaseUsers.metadata.create_all(engine_users)
BaseAdmins.metadata.create_all(engine_admins)
