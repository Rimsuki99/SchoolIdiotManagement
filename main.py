import pandas as pd
import numpy as np
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import hashlib

# ==========================================
# 1. AUTHENTICATION LOGIC
# ==========================================
class AuthSystem:
    def __init__(self):
        self.users_file = 'users.csv'
        self._initialize_file()

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

# ==========================================
# 2. DATA MANAGEMENT (Pandas)
# ==========================================
class AdminLogic:
    def __init__(self):
        self.emp_file = 'employees.csv'
        self.std_file = 'students.csv'
        self.cls_file = 'classes.csv'
        
        if not os.path.exists(self.emp_file):
            pd.DataFrame(columns=['ID', 'Name', 'Contact', 'Email', 'Position']).to_csv(self.emp_file, index=False)
            
        if not os.path.exists(self.std_file):
            pd.DataFrame(columns=['ID', 'Name', 'Age', 'Email', 'Class']).to_csv(self.std_file, index=False)
            
        if not os.path.exists(self.cls_file):
            # Added Day, Start Time, and End Time to the dataframe
            pd.DataFrame(columns=['Class Name', 'Lecturer ID', 'Lecturer Name', 'Day', 'Start Time', 'End Time']).to_csv(self.cls_file, index=False)

    # --- Employee Logic ---
    def get_all_employees(self):
        return pd.read_csv(self.emp_file)

    def generate_emp_id(self, position):
        df = pd.read_csv(self.emp_file)
        pos_df = df[df['Position'] == position]
        if pos_df.empty:
            return 2001 if position == "Lecturer" else 3001
        return int(pos_df['ID'].max()) + 1

    def add_employee(self, name, contact, email, position):
        df = pd.read_csv(self.emp_file)
        new_id = self.generate_emp_id(position)
        new_emp = pd.DataFrame([{'ID': new_id, 'Name': name, 'Contact': contact, 'Email': email, 'Position': position}])
        df = pd.concat([df, new_emp], ignore_index=True)
        df.to_csv(self.emp_file, index=False)
        return True, f"Employee Added!\nAuto-Assigned ID: {new_id}", new_id

    def remove_employee(self, emp_id):
        df = pd.read_csv(self.emp_file)
        emp_id = int(emp_id) 
        if emp_id not in df['ID'].values:
            return False, "Employee ID not found."
        df = df[df['ID'] != emp_id]
        df.to_csv(self.emp_file, index=False)
        return True, "Employee Removed!"
        
    def update_employee(self, emp_id, name, contact, email, position):
        df = pd.read_csv(self.emp_file)
        emp_id = int(emp_id) 
        df['Name'] = df['Name'].astype(str)
        df['Contact'] = df['Contact'].astype(str)
        df['Email'] = df['Email'].astype(str)
        df['Position'] = df['Position'].astype(str)
        
        if emp_id not in df['ID'].values:
            return False, "Employee ID not found."
        df.loc[df['ID'] == emp_id, ['Name', 'Contact', 'Email', 'Position']] = [name, contact, email, position]
        df.to_csv(self.emp_file, index=False)
        return True, "Employee Updated!"

    # --- Student Logic ---
    def get_all_students(self):
        return pd.read_csv(self.std_file)
        
    def generate_std_id(self):
        df = pd.read_csv(self.std_file)
        if df.empty: return 4001
        return int(df['ID'].max()) + 1

    def add_single_student(self, name, age, email, std_class):
        df = pd.read_csv(self.std_file)
        new_id = self.generate_std_id()
        new_std = pd.DataFrame([{'ID': new_id, 'Name': name, 'Age': age, 'Email': email, 'Class': std_class}])
        df = pd.concat([df, new_std], ignore_index=True)
        df.to_csv(self.std_file, index=False)
        return True, f"New Student Added!\nAuto-Assigned ID: {new_id}"

    def add_class_to_student(self, std_id, name, age, email, new_class):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)
        if not df[(df['ID'] == std_id) & (df['Class'] == new_class)].empty:
            return False, f"Student is already enrolled in {new_class}!"
        new_row = pd.DataFrame([{'ID': std_id, 'Name': name, 'Age': age, 'Email': email, 'Class': new_class}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.std_file, index=False)
        return True, f"Class {new_class} added to Student {std_id}!"

    def upload_student_csv(self, filepath):
        try:
            new_df = pd.read_csv(filepath)
            required_columns = ['Name', 'Age', 'Email', 'Class']
            if not all(col in new_df.columns for col in required_columns):
                return False, "CSV must contain columns: Name, Age, Email, Class"
            
            df = pd.read_csv(self.std_file)
            if 'ID' in new_df.columns:
                new_df = new_df.drop(columns=['ID'])
                
            added_count = 0
            for index, row in new_df.iterrows():
                name = str(row['Name']).strip()
                email = str(row['Email']).strip()
                age = str(row['Age']).strip()
                std_class = str(row['Class']).strip()
                
                if not df[(df['Email'] == email) & (df['Class'] == std_class)].empty:
                    continue 
                    
                existing_student = df[df['Email'] == email]
                if not existing_student.empty:
                    std_id = existing_student.iloc[0]['ID']
                else:
                    std_id = 4001 if df.empty else int(df['ID'].max()) + 1
                    
                new_row = pd.DataFrame([{'ID': std_id, 'Name': name, 'Age': age, 'Email': email, 'Class': std_class}])
                df = pd.concat([df, new_row], ignore_index=True)
                added_count += 1
                
            df.to_csv(self.std_file, index=False)
            if added_count == 0:
                return True, "No new records added. All students in the file already exist in those classes!"
            else:
                return True, f"Successfully imported {added_count} new student records!"
        except Exception as e:
            return False, f"Error processing file: {str(e)}"

    def update_student(self, std_id, name, age, email, old_class, new_class):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)
        df['Name'] = df['Name'].astype(str)
        df['Email'] = df['Email'].astype(str)
        df['Class'] = df['Class'].astype(str)
        
        if std_id not in df['ID'].values:
            return False, "Student ID not found."
            
        df.loc[df['ID'] == std_id, ['Name', 'Age', 'Email']] = [name, int(age), email]
        if old_class != new_class:
            df.loc[(df['ID'] == std_id) & (df['Class'] == old_class), 'Class'] = new_class
            
        df.to_csv(self.std_file, index=False)
        return True, "Student Record Updated!"

    def remove_student_class(self, std_id, class_name):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)
        df = df[~((df['ID'] == std_id) & (df['Class'] == class_name))]
        df.to_csv(self.std_file, index=False)
        return True, f"Class {class_name} removed for student {std_id}!"

    # --- Class & Schedule Logic ---
    def get_all_assignments(self):
        return pd.read_csv(self.cls_file)

    def assign_lecturer(self, class_name, lec_id, lec_name, day, start_time, end_time):
        df = pd.read_csv(self.cls_file)
        
        # Make sure the string data doesn't throw a Pandas error
        for col in ['Day', 'Start Time', 'End Time']:
            if col in df.columns:
                df[col] = df[col].astype(str)

        if class_name in df['Class Name'].values:
            df.loc[df['Class Name'] == class_name, ['Lecturer ID', 'Lecturer Name', 'Day', 'Start Time', 'End Time']] = [lec_id, lec_name, day, start_time, end_time]
            msg = "Class assignment updated to new schedule!"
        else:
            new_row = pd.DataFrame([{'Class Name': class_name, 'Lecturer ID': lec_id, 'Lecturer Name': lec_name, 'Day': day, 'Start Time': start_time, 'End Time': end_time}])
            df = pd.concat([df, new_row], ignore_index=True)
            msg = "Lecturer and schedule successfully assigned!"
            
        df.to_csv(self.cls_file, index=False)
        return True, msg

    def remove_assignment(self, class_name):
        df = pd.read_csv(self.cls_file)
        if class_name not in df['Class Name'].values:
            return False, "No assignment found for this class."
        df = df[df['Class Name'] != class_name]
        df.to_csv(self.cls_file, index=False)
        return True, "Assignment removed!"

# ==========================================
# 3. GRAPHICAL USER INTERFACE (GUI)
# ==========================================
class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("900x750") # Expanded slightly to fit the new schedule table
        
        self.auth = AuthSystem()
        self.admin_logic = AdminLogic()
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (LoginFrame, RegisterFrame, AdminDashboard):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
            
        self.show_frame("LoginFrame")
        
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "AdminDashboard":
            frame.refresh_employee_table()
            frame.refresh_student_table()
            frame.refresh_class_table()
        frame.tkraise()

# --- LOGIN & REGISTER FRAMES (Unchanged) ---
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.center_frame = tk.Frame(self)
        self.center_frame.pack(expand=True)
        tk.Label(self.center_frame, text="System Login", font=("Arial", 18, "bold")).pack(pady=(0, 20))
        tk.Label(self.center_frame, text="Select Role:").pack()
        self.role_var = tk.StringVar(value="Admin") 
        role_frame = tk.Frame(self.center_frame)
        role_frame.pack(pady=10)
        self.btn_admin = tk.Button(role_frame, text="Admin", width=12, command=lambda: self.set_role("Admin"))
        self.btn_admin.pack(side="left", padx=5)
        self.btn_lecturer = tk.Button(role_frame, text="Lecturer", width=12, command=lambda: self.set_role("Lecturer"))
        self.btn_lecturer.pack(side="left", padx=5)
        self.set_role("Admin")
        
        tk.Label(self.center_frame, text="Username:").pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.center_frame, width=30)
        self.username_entry.pack(pady=5)
        tk.Label(self.center_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.center_frame, show="*", width=30)
        self.password_entry.pack(pady=5)
        
        tk.Button(self.center_frame, text="Login", width=20, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.attempt_login).pack(pady=20)
        tk.Button(self.center_frame, text="Register New Admin", relief="flat", fg="blue", command=lambda: controller.show_frame("RegisterFrame")).pack()

    def set_role(self, role):
        self.role_var.set(role)
        if role == "Admin":
            self.btn_admin.config(relief="sunken", bg="lightgray")
            self.btn_lecturer.config(relief="raised", bg="SystemButtonFace")
        else:
            self.btn_admin.config(relief="raised", bg="SystemButtonFace")
            self.btn_lecturer.config(relief="sunken", bg="lightgray")

    def attempt_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        selected_role = self.role_var.get()
        if self.controller.auth.login(username, password, selected_role):
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            if selected_role == "Admin": self.controller.show_frame("AdminDashboard")
            else: messagebox.showinfo("WIP", "Lecturer Dashboard coming soon!")
        else:
            messagebox.showerror("Error", "Invalid credentials.")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.center_frame = tk.Frame(self)
        self.center_frame.pack(expand=True)
        tk.Label(self.center_frame, text="Admin Registration", font=("Arial", 18, "bold")).pack(pady=(0, 20))
        tk.Label(self.center_frame, text="Username:").pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.center_frame, width=30)
        self.username_entry.pack(pady=5)
        tk.Label(self.center_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.center_frame, show="*", width=30)
        self.password_entry.pack(pady=5)
        
        tk.Button(self.center_frame, text="Register", width=20, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.attempt_register).pack(pady=20)
        tk.Button(self.center_frame, text="Back to Login", relief="flat", fg="blue", command=lambda: controller.show_frame("LoginFrame")).pack()

    def attempt_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showwarning("Warning", "Fields cannot be empty!")
            return
        success, message = self.controller.auth.register_user(username, password, role="Admin")
        if success:
            messagebox.showinfo("Success", message)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.controller.show_frame("LoginFrame")
        else: messagebox.showerror("Error", message)

# --- ADMIN DASHBOARD ---
class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        header_frame = tk.Frame(self, bg="#333", height=50)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Admin Dashboard", fg="white", bg="#333", font=("Arial", 16, "bold")).pack(side="left", padx=10, pady=10)
        tk.Button(header_frame, text="Logout", command=lambda: controller.show_frame("LoginFrame")).pack(side="right", padx=10)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tab_employee = tk.Frame(self.notebook)
        self.notebook.add(self.tab_employee, text="Employee Management")
        self.setup_employee_tab()
        
        self.tab_student = tk.Frame(self.notebook)
        self.notebook.add(self.tab_student, text="Student Management")
        self.setup_student_tab()
        
        self.tab_class = tk.Frame(self.notebook)
        self.notebook.add(self.tab_class, text="Class Management")
        self.setup_class_tab()

    # ==========================
    # EMPLOYEE TAB METHODS
    # ==========================
    def setup_employee_tab(self):
        form_frame = tk.Frame(self.tab_employee)
        form_frame.pack(fill="x", pady=10)
        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_emp_id = tk.Entry(form_frame, width=10, state="readonly")
        self.ent_emp_id.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_emp_name = tk.Entry(form_frame, width=20)
        self.ent_emp_name.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Contact:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_emp_contact = tk.Entry(form_frame, width=15)
        self.ent_emp_contact.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Email:").grid(row=1, column=2, padx=5, pady=5)
        self.ent_emp_email = tk.Entry(form_frame, width=20)
        self.ent_emp_email.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Position:").grid(row=2, column=0, padx=5, pady=5)
        self.cmb_emp_position = ttk.Combobox(form_frame, values=["Lecturer", "Staff"], width=13, state="readonly")
        self.cmb_emp_position.grid(row=2, column=1, padx=5, pady=5)
        self.cmb_emp_position.set("Lecturer")
        
        btn_frame = tk.Frame(self.tab_employee)
        btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Add Employee", bg="#4CAF50", fg="white", command=self.add_emp).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Selected", bg="#2196F3", fg="white", command=self.update_emp).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected", bg="#f44336", fg="white", command=self.remove_emp).pack(side="left", padx=5)
        
        self.tree_emp = ttk.Treeview(self.tab_employee, columns=("ID", "Name", "Contact", "Email", "Position"), show="headings")
        for col in ("ID", "Name", "Contact", "Email", "Position"):
            self.tree_emp.heading(col, text=col)
        self.tree_emp.column("ID", width=50)
        self.tree_emp.pack(fill="both", expand=True, pady=10)
        self.tree_emp.bind("<<TreeviewSelect>>", self.on_employee_select)

    def refresh_employee_table(self):
        for item in self.tree_emp.get_children(): self.tree_emp.delete(item)
        df = self.controller.admin_logic.get_all_employees()
        for _, row in df.iterrows():
            self.tree_emp.insert("", "end", values=(row['ID'], row['Name'], row['Contact'], row['Email'], row['Position']))

    def on_employee_select(self, event):
        selected = self.tree_emp.selection()
        if not selected: return
        values = self.tree_emp.item(selected[0], 'values')
        if values:
            self.ent_emp_id.config(state="normal")
            self.ent_emp_id.delete(0, tk.END); self.ent_emp_name.delete(0, tk.END)
            self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.ent_emp_id.insert(0, values[0]); self.ent_emp_name.insert(0, values[1])
            self.ent_emp_contact.insert(0, values[2]); self.ent_emp_email.insert(0, values[3])
            self.cmb_emp_position.set(values[4])
            self.ent_emp_id.config(state="readonly")

    def add_emp(self):
        name = self.ent_emp_name.get()
        contact = self.ent_emp_contact.get()
        email = self.ent_emp_email.get()
        position = self.cmb_emp_position.get()
        if not all([name, contact, email, position]):
            return messagebox.showwarning("Warning", "All fields are required!")
        success, msg, new_id = self.controller.admin_logic.add_employee(name, contact, email, position)
        if success:
            if position == "Lecturer":
                gen_username = f"{new_id}_{name.split()[0]}"
                gen_password = "password123"
                self.controller.auth.register_user(gen_username, gen_password, role="Lecturer")
                msg += f"\n\nLecturer Login Created:\nUser: {gen_username}\nPass: {gen_password}"
            messagebox.showinfo("Success", msg)
            self.ent_emp_name.delete(0, tk.END); self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.refresh_employee_table()
            self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def update_emp(self):
        emp_id = self.ent_emp_id.get()
        if not emp_id: return messagebox.showwarning("Warning", "Select an employee first!")
        name = self.ent_emp_name.get()
        contact = self.ent_emp_contact.get()
        email = self.ent_emp_email.get()
        position = self.cmb_emp_position.get()
        success, msg = self.controller.admin_logic.update_employee(emp_id, name, contact, email, position)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_employee_table()
            self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def remove_emp(self):
        emp_id = self.ent_emp_id.get()
        if not emp_id: return messagebox.showwarning("Warning", "Select an employee first!")
        success, msg = self.controller.admin_logic.remove_employee(emp_id)
        if success:
            self.controller.auth.remove_account_by_id(emp_id)
            messagebox.showinfo("Success", msg)
            self.ent_emp_id.config(state="normal"); self.ent_emp_id.delete(0, tk.END); self.ent_emp_id.config(state="readonly")
            self.ent_emp_name.delete(0, tk.END); self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.refresh_employee_table()
            self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    # ==========================
    # STUDENT TAB METHODS
    # ==========================
    def setup_student_tab(self):
        self.selected_old_class = None 
        upload_frame = tk.Frame(self.tab_student, bg="#f0f0f0", bd=1, relief="solid")
        upload_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(upload_frame, text="Batch Data Upload:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=10, pady=10)
        tk.Button(upload_frame, text="Upload Student CSV", bg="#607D8B", fg="white", command=self.upload_csv).pack(side="left", padx=10)
        
        form_frame = tk.Frame(self.tab_student)
        form_frame.pack(fill="x", pady=10, padx=10)
        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5)
        self.ent_std_id = tk.Entry(form_frame, width=10, state="readonly")
        self.ent_std_id.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5)
        self.ent_std_name = tk.Entry(form_frame, width=20)
        self.ent_std_name.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Age:").grid(row=0, column=4, padx=5, pady=5)
        self.ent_std_age = tk.Entry(form_frame, width=10)
        self.ent_std_age.grid(row=0, column=5, padx=5, pady=5)
        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_std_email = tk.Entry(form_frame, width=25)
        self.ent_std_email.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        
        tk.Label(form_frame, text="Class:").grid(row=1, column=3, padx=5, pady=5)
        self.ent_std_class = ttk.Combobox(form_frame, values=[
            "BIC3104 Programming for Computer Science", 
            "BIC3133 Object Oriented Methods", 
            "BIC3223 Network Security Design", 
            "BIC3253 Entrepreneurship", 
            "BIC2283 Business Systems Development Tools", 
            "BIC3163 Application Layer Programming"
        ], width=45, state="readonly")
        self.ent_std_class.grid(row=1, column=4, columnspan=2, sticky="w", padx=5, pady=5)
        self.ent_std_class.set("BIC3104 Programming for Computer Science")
        
        btn_frame = tk.Frame(self.tab_student)
        btn_frame.pack(fill="x", pady=5, padx=10)
        tk.Button(btn_frame, text="Add New Student", bg="#4CAF50", fg="white", command=self.add_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Class to Selected", bg="#8BC34A", fg="black", command=self.add_class_to_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Selected", bg="#2196F3", fg="white", command=self.update_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected Class", bg="#f44336", fg="white", command=self.remove_std).pack(side="left", padx=5)
        
        self.tree_std = ttk.Treeview(self.tab_student, columns=("ID", "Name", "Age", "Email", "Class"), show="headings")
        for col in ("ID", "Name", "Age", "Email", "Class"):
            self.tree_std.heading(col, text=col)
        self.tree_std.column("ID", width=50); self.tree_std.column("Age", width=50)
        self.tree_std.pack(fill="both", expand=True, pady=10, padx=10)
        self.tree_std.bind("<<TreeviewSelect>>", self.on_student_select)

    def refresh_student_table(self):
        for item in self.tree_std.get_children(): self.tree_std.delete(item)
        df = self.controller.admin_logic.get_all_students()
        for _, row in df.iterrows():
            self.tree_std.insert("", "end", values=(row['ID'], row['Name'], row['Age'], row['Email'], row['Class']))

    def on_student_select(self, event):
        selected = self.tree_std.selection()
        if not selected: return
        values = self.tree_std.item(selected[0], 'values')
        if values:
            self.ent_std_id.config(state="normal")
            self.ent_std_id.delete(0, tk.END); self.ent_std_name.delete(0, tk.END)
            self.ent_std_age.delete(0, tk.END); self.ent_std_email.delete(0, tk.END)
            self.ent_std_id.insert(0, values[0]); self.ent_std_name.insert(0, values[1])
            self.ent_std_age.insert(0, values[2]); self.ent_std_email.insert(0, values[3])
            self.ent_std_class.set(values[4])
            self.selected_old_class = values[4] 
            self.ent_std_id.config(state="readonly")

    def upload_csv(self):
        filepath = filedialog.askopenfilename(title="Select Student CSV", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if not filepath: return
        success, msg = self.controller.admin_logic.upload_student_csv(filepath)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def add_std(self):
        name = self.ent_std_name.get(); age = self.ent_std_age.get()
        email = self.ent_std_email.get(); std_class = self.ent_std_class.get()
        if not all([name, age, email, std_class]): return messagebox.showwarning("Warning", "All fields required!")
        if not age.isdigit(): return messagebox.showwarning("Warning", "Age must be a number!")
        success, msg = self.controller.admin_logic.add_single_student(name, age, email, std_class)
        messagebox.showinfo("Success", msg)
        self.refresh_student_table()

    def add_class_to_std(self):
        std_id = self.ent_std_id.get()
        if not std_id: return messagebox.showwarning("Warning", "Select an existing student first!")
        name = self.ent_std_name.get(); age = self.ent_std_age.get()
        email = self.ent_std_email.get(); new_class = self.ent_std_class.get()
        if not all([name, age, email, new_class]): return messagebox.showwarning("Warning", "All fields required!")
        success, msg = self.controller.admin_logic.add_class_to_student(std_id, name, age, email, new_class)
        if success:
            messagebox.showinfo("Success", msg)
            self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def update_std(self):
        std_id = self.ent_std_id.get()
        if not std_id: return messagebox.showwarning("Warning", "Select a student first!")
        name = self.ent_std_name.get(); age = self.ent_std_age.get()
        email = self.ent_std_email.get(); new_class = self.ent_std_class.get()
        if not age.isdigit(): return messagebox.showwarning("Warning", "Age must be a number!")
        success, msg = self.controller.admin_logic.update_student(std_id, name, age, email, self.selected_old_class, new_class)
        if success:
            messagebox.showinfo("Success", msg)
            self.selected_old_class = new_class 
            self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def remove_std(self):
        std_id = self.ent_std_id.get()
        if not std_id: return messagebox.showwarning("Warning", "Select a student first!")
        success, msg = self.controller.admin_logic.remove_student_class(std_id, self.selected_old_class)
        if success:
            messagebox.showinfo("Success", msg)
            self.ent_std_id.config(state="normal"); self.ent_std_id.delete(0, tk.END); self.ent_std_id.config(state="readonly")
            self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    # ==========================
    # CLASS MANAGEMENT TAB 
    # ==========================
    def setup_class_tab(self):
        form_frame = tk.Frame(self.tab_class)
        form_frame.pack(fill="x", pady=20, padx=10)
        
        # ROW 0: Select Class
        tk.Label(form_frame, text="Select Class:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.cmb_assign_class = ttk.Combobox(form_frame, values=[
            "BIC3104 Programming for Computer Science", 
            "BIC3133 Object Oriented Methods", 
            "BIC3223 Network Security Design", 
            "BIC3253 Entrepreneurship", 
            "BIC2283 Business Systems Development Tools", 
            "BIC3163 Application Layer Programming"
        ], width=45, state="readonly")
        self.cmb_assign_class.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # ROW 1: Select Lecturer
        tk.Label(form_frame, text="Select Lecturer:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.cmb_assign_lec = ttk.Combobox(form_frame, width=45, state="readonly")
        self.cmb_assign_lec.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # ROW 2: Day Selection
        tk.Label(form_frame, text="Day:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cmb_day = ttk.Combobox(form_frame, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], width=20, state="readonly")
        self.cmb_day.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # Generate the time list (1:00, 1:30, 2:00... 12:30)
        time_vals = [f"{h}:{m:02d}" for h in range(1, 13) for m in (0, 30)]
        
        # ROW 3: Start Time 
        tk.Label(form_frame, text="Start Time:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        start_frame = tk.Frame(form_frame)
        start_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        self.cmb_start_time = ttk.Combobox(start_frame, values=time_vals, width=8, state="readonly")
        self.cmb_start_time.pack(side="left", padx=(0, 5))
        self.cmb_start_ampm = ttk.Combobox(start_frame, values=["AM", "PM"], width=5, state="readonly")
        self.cmb_start_ampm.pack(side="left")
        
        # ROW 4: End Time
        tk.Label(form_frame, text="End Time:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        end_frame = tk.Frame(form_frame)
        end_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        self.cmb_end_time = ttk.Combobox(end_frame, values=time_vals, width=8, state="readonly")
        self.cmb_end_time.pack(side="left", padx=(0, 5))
        self.cmb_end_ampm = ttk.Combobox(end_frame, values=["AM", "PM"], width=5, state="readonly")
        self.cmb_end_ampm.pack(side="left")
        
        # Action Buttons
        btn_frame = tk.Frame(self.tab_class)
        btn_frame.pack(fill="x", pady=5, padx=10)
        tk.Button(btn_frame, text="Assign Schedule", bg="#4CAF50", fg="white", command=self.assign_lec).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Schedule", bg="#f44336", fg="white", command=self.remove_assign).pack(side="left", padx=5)
        
        # Updated Treeview with new schedule columns
        self.tree_class = ttk.Treeview(self.tab_class, columns=("Class Name", "Lecturer ID", "Lecturer Name", "Day", "Start Time", "End Time"), show="headings")
        for col in ("Class Name", "Lecturer ID", "Lecturer Name", "Day", "Start Time", "End Time"):
            self.tree_class.heading(col, text=col)
        
        self.tree_class.column("Lecturer ID", width=80)
        self.tree_class.column("Day", width=80)
        self.tree_class.column("Start Time", width=80)
        self.tree_class.column("End Time", width=80)
        self.tree_class.pack(fill="both", expand=True, pady=10, padx=10)
        
        self.tree_class.bind("<<TreeviewSelect>>", self.on_class_select)

    def refresh_class_table(self):
        for item in self.tree_class.get_children(): self.tree_class.delete(item)
        df = self.controller.admin_logic.get_all_assignments()
        for _, row in df.iterrows():
            self.tree_class.insert("", "end", values=(
                row.get('Class Name', ''), 
                row.get('Lecturer ID', ''), 
                row.get('Lecturer Name', ''),
                row.get('Day', ''),
                row.get('Start Time', ''),
                row.get('End Time', '')
            ))
            
        emp_df = self.controller.admin_logic.get_all_employees()
        lecturers = emp_df[emp_df['Position'] == 'Lecturer']
        lec_list = []
        for _, row in lecturers.iterrows():
            lec_list.append(f"{row['ID']} - {row['Name']}")
            
        self.cmb_assign_lec['values'] = lec_list

    def on_class_select(self, event):
        selected = self.tree_class.selection()
        if not selected: return
        values = self.tree_class.item(selected[0], 'values')
        if values:
            self.cmb_assign_class.set(values[0])
            self.cmb_assign_lec.set(f"{values[1]} - {values[2]}")
            self.cmb_day.set(values[3])
            
            # Split the "10:00 AM" back into the time dropdown and AM/PM dropdown
            if values[4]:
                start_parts = values[4].split(" ")
                if len(start_parts) == 2:
                    self.cmb_start_time.set(start_parts[0])
                    self.cmb_start_ampm.set(start_parts[1])
            
            if values[5]:
                end_parts = values[5].split(" ")
                if len(end_parts) == 2:
                    self.cmb_end_time.set(end_parts[0])
                    self.cmb_end_ampm.set(end_parts[1])

    def assign_lec(self):
        cls_name = self.cmb_assign_class.get()
        lec_val = self.cmb_assign_lec.get()
        day = self.cmb_day.get()
        
        start_t = self.cmb_start_time.get()
        start_ap = self.cmb_start_ampm.get()
        
        end_t = self.cmb_end_time.get()
        end_ap = self.cmb_end_ampm.get()
        
        if not all([cls_name, lec_val, day, start_t, start_ap, end_t, end_ap]):
            return messagebox.showwarning("Warning", "Please completely fill out the schedule and assignment!")
            
        # Combine the time and AM/PM strings for clean storage
        full_start_time = f"{start_t} {start_ap}"
        full_end_time = f"{end_t} {end_ap}"
            
        lec_id, lec_name = lec_val.split(" - ", 1)
        
        success, msg = self.controller.admin_logic.assign_lecturer(
            cls_name, lec_id, lec_name, day, full_start_time, full_end_time
        )
        
        messagebox.showinfo("Success", msg)
        self.refresh_class_table()

    def remove_assign(self):
        cls_name = self.cmb_assign_class.get()
        if not cls_name:
            return messagebox.showwarning("Warning", "Select an assignment to remove first!")
            
        success, msg = self.controller.admin_logic.remove_assignment(cls_name)
        if success:
            messagebox.showinfo("Success", msg)
            self.cmb_assign_class.set("")
            self.cmb_assign_lec.set("")
            self.cmb_day.set("")
            self.cmb_start_time.set("")
            self.cmb_start_ampm.set("")
            self.cmb_end_time.set("")
            self.cmb_end_ampm.set("")
            self.refresh_class_table()
        else:
            messagebox.showerror("Error", msg)

# ==========================================
# 4. RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()