from typing import List

from .models import Admin
from .configurator import SessionAdmins


class AdminsControl:
    """Controller for managing bot administrators using SQLAlchemy ORM."""

    def is_admin(self, admin_id: int) -> bool:
        """Check if a user ID belongs to an admin.

        Args:
            admin_id (int): Telegram user ID.

        Returns:
            bool: True if admin, False otherwise.
        """
        with SessionAdmins() as session:
            admin = session.query(Admin).filter(Admin.user_id == admin_id).first()
            return admin is not None

    def get_admins(self, status: str = "external") -> List[int]:
        """Get a list of admin user IDs filtered by status.

        Args:
            status (str): Admin status to filter ('external' or 'include').

        Returns:
            List[int]: List of user IDs.
        """
        with SessionAdmins() as session:
            admins = session.query(Admin.user_id).filter(Admin.status == status).all()
            return [a[0] for a in admins]

    def add_admin(self, admin_id: int, status: str = "external") -> bool:
        """Add a new admin if they do not already exist.

        Args:
            admin_id (int): Telegram user ID.
            status (str): Status of the admin ('external' or 'include').

        Returns:
            bool: True if added successfully, False if already exists.
        """
        if self.is_admin(admin_id):
            return False

        with SessionAdmins() as session:
            new_admin = Admin(user_id=admin_id, status=status)
            session.add(new_admin)
            session.commit()
            return True

    def del_admin(self, admin_id: int) -> bool:
        """Delete an admin by user ID.

        Args:
            admin_id (int): Telegram user ID.

        Returns:
            bool: True if deleted, False if admin not found.
        """
        with SessionAdmins() as session:
            admin = session.query(Admin).filter(Admin.user_id == admin_id).first()
            if not admin:
                return False

            session.delete(admin)
            session.commit()
            return True
