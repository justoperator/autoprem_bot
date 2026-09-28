from app.database import AdminsControl

admins = AdminsControl()


new_admin = int(input('Enter new admin id: ').strip())
admins.add_admin(new_admin, 'include')
