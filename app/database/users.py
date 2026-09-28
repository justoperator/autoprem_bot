from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlalchemy import func

from .models import User
from .configurator import SessionUsers


class UsersControl:
    """Controller for managing bot users using SQLAlchemy ORM."""

    def is_exists(self, user_id: int) -> bool:
        """Check if a user exists in the database.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        with SessionUsers() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            return user is not None

    def add_user(
        self,
        user_id: int,
        username: str,
        f_name: str,
        l_name: str,
        lang_code: str
    ) -> None:
        """Add a new user if they do not already exist.

        Args:
            user_id (int): Telegram user ID.
            username (str): Telegram username.
            f_name (str): First name.
            l_name (str): Last name.
            lang_code (str): Language code.
        """
        if self.is_exists(user_id):
            return

        now = datetime.now()

        with SessionUsers() as session:
            new_user = User(
                user_id=user_id,
                username=username,
                first_name=f_name,
                last_name=l_name,
                reg_date=now,
                lang_code=lang_code
            )
            session.add(new_user)
            session.commit()

    def get_user_for_stat(self, user_id: int) -> Optional[Tuple]:
        """Get full information about a specific user.

        Args:
            user_id (int): Telegram user ID.

        Returns:
            Optional[Tuple]: Tuple with (user_id, username, first_name,
                last_name, reg_date, lang_code) or None if not found.
        """
        with SessionUsers() as session:
            user = session.query(User).filter(User.user_id == user_id).first()
            if not user:
                return None

            return (
                user.user_id,
                user.username,
                user.first_name,
                user.last_name,
                user.reg_date.strftime('%d-%m-%Y %H:%M'),
                user.lang_code
            )

    def get_users_for_stat(self) -> Tuple[int, List[Tuple[str, str]], int, int]:
        """Get aggregated statistics about users.

        Returns:
            Tuple containing:
                - total_count (int): Total number of users.
                - all_users (List[Tuple[str, str]]): List of (first_name,
                  registration_date) for all users.
                - last_week_count (int): Number of users registered in the
                  last 7 days.
                - last_month_count (int): Number of users registered in the
                  last 30 days.
        """
        with SessionUsers() as session:
            total_count = session.query(func.count(User.id)).scalar()

            now = datetime.now()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)

            last_week_count = session.query(func.count(User.id))\
                .filter(User.reg_date >= week_ago).scalar()

            last_month_count = session.query(func.count(User.id))\
                .filter(User.reg_date >= month_ago).scalar()

            all_users_query = session.query(User.user_id, User.first_name, User.reg_date).all()
            all_users = [
                (u.user_id, u.first_name, u.reg_date.strftime('%d-%m-%Y %H:%M'))
                for u in all_users_query
            ]

            return total_count, all_users, last_week_count, last_month_count
