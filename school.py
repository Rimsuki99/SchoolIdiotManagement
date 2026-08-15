import pandas as pd
import os
import hashlib

from admin import Admin
from teacher import Teacher

# ==========================================
# SCHOOL: Central system integrating all functionalities
# ==========================================
class School:
    def __init__(self):
        self.users_file = 'users.csv'
        self._initialize_file()
        self.admin = Admin()
        self.teacher = Teacher()

    def _initialize_file(self):
        if not os.path.exists(self.users_file):
            df = pd.DataFrame(columns=['Username', 'Password', 'Role'])
            df.to_csv(self.users_file, index=False)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password, role="Admin"):
        df = pd.read_csv(self.users_file)
        if username in df['Username'].values:
            return False, "Username already exists!"

        hashed_password = self._hash_password(password)
        new_user = pd.DataFrame([{'Username': username, 'Password': hashed_password, 'Role': role}])
        df = pd.concat([df, new_user], ignore_index=True)
        df.to_csv(self.users_file, index=False)
        return True, f"{role} registered successfully!"

    def login(self, username, password, selected_role):
        df = pd.read_csv(self.users_file)
        hashed_attempt = self._hash_password(password)
        user = df[(df['Username'] == username) &
                  (df['Password'] == hashed_attempt) &
                  (df['Role'] == selected_role)]

        if not user.empty:
            return True
        return False

    def remove_account_by_id(self, emp_id):
        df = pd.read_csv(self.users_file)
        prefix = f"{emp_id}_"
        df = df[~df['Username'].astype(str).str.startswith(prefix)]
        df.to_csv(self.users_file, index=False)
