import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from school import School

# ==========================================
# GRAPHICAL USER INTERFACE (GUI)
# ==========================================
class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("950x750") 
        
        self.school = School()
        self.current_user_id = None 
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        self.frames = {}
        for F in (LoginFrame, RegisterFrame, AdminDashboard, LecturerDashboard):
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
            frame.refresh_employee_table(); frame.refresh_student_table(); frame.refresh_class_table()
        elif page_name == "LecturerDashboard":
            frame.setup_lecturer_data() 
        frame.tkraise()

# --- Login & Registration ---
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.center_frame = tk.Frame(self); self.center_frame.pack(expand=True)
        tk.Label(self.center_frame, text="System Login", font=("Arial", 18, "bold")).pack(pady=(0, 20))
        tk.Label(self.center_frame, text="Select Role:").pack()
        self.role_var = tk.StringVar(value="Admin"); role_frame = tk.Frame(self.center_frame); role_frame.pack(pady=10)
        self.btn_admin = tk.Button(role_frame, text="Admin", width=12, command=lambda: self.set_role("Admin")); self.btn_admin.pack(side="left", padx=5)
        self.btn_lecturer = tk.Button(role_frame, text="Lecturer", width=12, command=lambda: self.set_role("Lecturer")); self.btn_lecturer.pack(side="left", padx=5)
        self.set_role("Admin")
        tk.Label(self.center_frame, text="Username:").pack(pady=(10, 0)); self.username_entry = tk.Entry(self.center_frame, width=30); self.username_entry.pack(pady=5)
        tk.Label(self.center_frame, text="Password:").pack(); self.password_entry = tk.Entry(self.center_frame, show="*", width=30); self.password_entry.pack(pady=5)
        tk.Button(self.center_frame, text="Login", width=20, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=self.attempt_login).pack(pady=20)
        tk.Button(self.center_frame, text="Register New Admin", relief="flat", fg="blue", command=lambda: controller.show_frame("RegisterFrame")).pack()

    def set_role(self, role):
        self.role_var.set(role)
        if role == "Admin": self.btn_admin.config(relief="sunken", bg="lightgray"); self.btn_lecturer.config(relief="raised", bg="SystemButtonFace")
        else: self.btn_admin.config(relief="raised", bg="SystemButtonFace"); self.btn_lecturer.config(relief="sunken", bg="lightgray")

    def attempt_login(self):
        username = self.username_entry.get(); password = self.password_entry.get(); selected_role = self.role_var.get()
        if self.controller.school.login(username, password, selected_role):
            self.username_entry.delete(0, tk.END); self.password_entry.delete(0, tk.END)
            if selected_role == "Admin": self.controller.show_frame("AdminDashboard")
            else: 
                try:
                    self.controller.current_user_id = int(username.split("_")[0]); self.controller.show_frame("LecturerDashboard")
                except: messagebox.showerror("Error", "Corrupted Lecturer Username format.")
        else: messagebox.showerror("Error", "Invalid credentials.")

class RegisterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.center_frame = tk.Frame(self); self.center_frame.pack(expand=True)
        tk.Label(self.center_frame, text="Admin Registration", font=("Arial", 18, "bold")).pack(pady=(0, 20))
        tk.Label(self.center_frame, text="Username:").pack(pady=(10, 0)); self.username_entry = tk.Entry(self.center_frame, width=30); self.username_entry.pack(pady=5)
        tk.Label(self.center_frame, text="Password:").pack(); self.password_entry = tk.Entry(self.center_frame, show="*", width=30); self.password_entry.pack(pady=5)
        tk.Button(self.center_frame, text="Register", width=20, bg="#2196F3", fg="white", font=("Arial", 10, "bold"), command=self.attempt_register).pack(pady=20)
        tk.Button(self.center_frame, text="Back to Login", relief="flat", fg="blue", command=lambda: controller.show_frame("LoginFrame")).pack()

    def attempt_register(self):
        if not self.username_entry.get() or not self.password_entry.get(): return messagebox.showwarning("Warning", "Fields cannot be empty!")
        success, msg = self.controller.school.register_user(self.username_entry.get(), self.password_entry.get(), role="Admin")
        if success: messagebox.showinfo("Success", msg); self.username_entry.delete(0, tk.END); self.password_entry.delete(0, tk.END); self.controller.show_frame("LoginFrame")
        else: messagebox.showerror("Error", msg)

# --- Admin Dashboard ---
class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        header_frame = tk.Frame(self, bg="#333", height=50); header_frame.pack(fill="x")
        tk.Label(header_frame, text="Admin Dashboard", fg="white", bg="#333", font=("Arial", 16, "bold")).pack(side="left", padx=10, pady=10)
        tk.Button(header_frame, text="Logout", command=lambda: controller.show_frame("LoginFrame")).pack(side="right", padx=10)
        
        self.notebook = ttk.Notebook(self); self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_employee = tk.Frame(self.notebook); self.notebook.add(self.tab_employee, text="Employee Management"); self.setup_employee_tab()
        self.tab_student = tk.Frame(self.notebook); self.notebook.add(self.tab_student, text="Student Management"); self.setup_student_tab()
        self.tab_class = tk.Frame(self.notebook); self.notebook.add(self.tab_class, text="Class Management"); self.setup_class_tab()
        self.tab_analytics = tk.Frame(self.notebook); self.notebook.add(self.tab_analytics, text="Analytics & Reports"); self.setup_analytics_tab()

    def setup_employee_tab(self):
        form_frame = tk.Frame(self.tab_employee); form_frame.pack(fill="x", pady=10)
        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5); self.ent_emp_id = tk.Entry(form_frame, width=10, state="readonly"); self.ent_emp_id.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5); self.ent_emp_name = tk.Entry(form_frame, width=20); self.ent_emp_name.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Contact:").grid(row=1, column=0, padx=5, pady=5); self.ent_emp_contact = tk.Entry(form_frame, width=15); self.ent_emp_contact.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Email:").grid(row=1, column=2, padx=5, pady=5); self.ent_emp_email = tk.Entry(form_frame, width=20); self.ent_emp_email.grid(row=1, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Position:").grid(row=2, column=0, padx=5, pady=5); self.cmb_emp_position = ttk.Combobox(form_frame, values=["Lecturer", "Staff"], width=13, state="readonly"); self.cmb_emp_position.grid(row=2, column=1, padx=5, pady=5); self.cmb_emp_position.set("Lecturer")
        
        btn_frame = tk.Frame(self.tab_employee); btn_frame.pack(fill="x", pady=5)
        tk.Button(btn_frame, text="Add Employee", bg="#4CAF50", fg="white", command=self.add_emp).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Selected", bg="#2196F3", fg="white", command=self.update_emp).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected", bg="#f44336", fg="white", command=self.remove_emp).pack(side="left", padx=5)
        
        self.tree_emp = ttk.Treeview(self.tab_employee, columns=("ID", "Name", "Contact", "Email", "Position"), show="headings")
        for col in ("ID", "Name", "Contact", "Email", "Position"): self.tree_emp.heading(col, text=col)
        self.tree_emp.column("ID", width=50); self.tree_emp.pack(fill="both", expand=True, pady=10); self.tree_emp.bind("<<TreeviewSelect>>", self.on_employee_select)

    def refresh_employee_table(self):
        for item in self.tree_emp.get_children(): self.tree_emp.delete(item)
        for _, row in self.controller.school.admin.get_all_employees().iterrows(): self.tree_emp.insert("", "end", values=(row['ID'], row['Name'], row['Contact'], row['Email'], row['Position']))

    def on_employee_select(self, event):
        selected = self.tree_emp.selection()
        if not selected: return
        values = self.tree_emp.item(selected[0], 'values')
        if values:
            self.ent_emp_id.config(state="normal"); self.ent_emp_id.delete(0, tk.END); self.ent_emp_name.delete(0, tk.END); self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.ent_emp_id.insert(0, values[0]); self.ent_emp_name.insert(0, values[1]); self.ent_emp_contact.insert(0, values[2]); self.ent_emp_email.insert(0, values[3]); self.cmb_emp_position.set(values[4]); self.ent_emp_id.config(state="readonly")

    def add_emp(self):
        name = self.ent_emp_name.get(); contact = self.ent_emp_contact.get(); email = self.ent_emp_email.get(); position = self.cmb_emp_position.get()
        if not all([name, contact, email, position]): return messagebox.showwarning("Warning", "All fields are required!")
        success, msg, new_id = self.controller.school.admin.add_employee(name, contact, email, position)
        if success:
            if position == "Lecturer":
                gen_username = f"{new_id}_{name.split()[0]}"
                self.controller.school.register_user(gen_username, "password123", role="Lecturer")
                msg += f"\n\nLecturer Login Created:\nUser: {gen_username}\nPass: password123"
            messagebox.showinfo("Success", msg); self.ent_emp_name.delete(0, tk.END); self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.refresh_employee_table(); self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def update_emp(self):
        if not self.ent_emp_id.get(): return messagebox.showwarning("Warning", "Select an employee first!")
        success, msg = self.controller.school.admin.update_employee(self.ent_emp_id.get(), self.ent_emp_name.get(), self.ent_emp_contact.get(), self.ent_emp_email.get(), self.cmb_emp_position.get())
        if success: messagebox.showinfo("Success", msg); self.refresh_employee_table(); self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def remove_emp(self):
        if not self.ent_emp_id.get(): return messagebox.showwarning("Warning", "Select an employee first!")
        success, msg = self.controller.school.admin.remove_employee(self.ent_emp_id.get())
        if success:
            self.controller.school.remove_account_by_id(self.ent_emp_id.get()); messagebox.showinfo("Success", msg)
            self.ent_emp_id.config(state="normal"); self.ent_emp_id.delete(0, tk.END); self.ent_emp_id.config(state="readonly"); self.ent_emp_name.delete(0, tk.END); self.ent_emp_contact.delete(0, tk.END); self.ent_emp_email.delete(0, tk.END)
            self.refresh_employee_table(); self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def setup_student_tab(self):
        self.selected_old_class = None 
        upload_frame = tk.Frame(self.tab_student, bg="#f0f0f0", bd=1, relief="solid"); upload_frame.pack(fill="x", padx=10, pady=10)
        tk.Label(upload_frame, text="Batch Data Upload:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(side="left", padx=10, pady=10)
        tk.Button(upload_frame, text="Upload Student CSV", bg="#607D8B", fg="white", command=self.upload_csv).pack(side="left", padx=10)
        
        form_frame = tk.Frame(self.tab_student); form_frame.pack(fill="x", pady=10, padx=10)
        tk.Label(form_frame, text="ID (Auto):").grid(row=0, column=0, padx=5, pady=5); self.ent_std_id = tk.Entry(form_frame, width=10, state="readonly"); self.ent_std_id.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="Name:").grid(row=0, column=2, padx=5, pady=5); self.ent_std_name = tk.Entry(form_frame, width=20); self.ent_std_name.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(form_frame, text="Age:").grid(row=0, column=4, padx=5, pady=5); self.ent_std_age = tk.Entry(form_frame, width=10); self.ent_std_age.grid(row=0, column=5, padx=5, pady=5)
        tk.Label(form_frame, text="Email:").grid(row=1, column=0, padx=5, pady=5); self.ent_std_email = tk.Entry(form_frame, width=25); self.ent_std_email.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
        tk.Label(form_frame, text="Class:").grid(row=1, column=3, padx=5, pady=5)
        self.ent_std_class = ttk.Combobox(form_frame, values=["BIC3104 Programming for Computer Science", "BIC3133 Object Oriented Methods", "BIC3223 Network Security Design", "BIC3253 Entrepreneurship", "BIC2283 Business Systems Development Tools", "BIC3163 Application Layer Programming"], width=45, state="readonly")
        self.ent_std_class.grid(row=1, column=4, columnspan=2, sticky="w", padx=5, pady=5); self.ent_std_class.set("BIC3104 Programming for Computer Science")
        
        btn_frame = tk.Frame(self.tab_student); btn_frame.pack(fill="x", pady=5, padx=10)
        tk.Button(btn_frame, text="Add New Student", bg="#4CAF50", fg="white", command=self.add_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Add Class to Selected", bg="#8BC34A", fg="black", command=self.add_class_to_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update Selected", bg="#2196F3", fg="white", command=self.update_std).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Selected Class", bg="#f44336", fg="white", command=self.remove_std).pack(side="left", padx=5)
        
        self.tree_std = ttk.Treeview(self.tab_student, columns=("ID", "Name", "Age", "Email", "Class", "Grade", "Attendance"), show="headings")
        for col in ("ID", "Name", "Age", "Email", "Class", "Grade", "Attendance"): self.tree_std.heading(col, text=col)
        self.tree_std.column("ID", width=50); self.tree_std.column("Age", width=50); self.tree_std.column("Grade", width=50); self.tree_std.column("Attendance", width=80)
        self.tree_std.pack(fill="both", expand=True, pady=10, padx=10); self.tree_std.bind("<<TreeviewSelect>>", self.on_student_select)

    def refresh_student_table(self):
        for item in self.tree_std.get_children(): self.tree_std.delete(item)
        for _, row in self.controller.school.admin.get_all_students().iterrows():
            self.tree_std.insert("", "end", values=(row.get('ID',''), row.get('Name',''), row.get('Age',''), row.get('Email',''), row.get('Class',''), row.get('Grade',''), row.get('Attendance','')))

    def on_student_select(self, event):
        selected = self.tree_std.selection()
        if not selected: return
        values = self.tree_std.item(selected[0], 'values')
        if values:
            self.ent_std_id.config(state="normal"); self.ent_std_id.delete(0, tk.END); self.ent_std_name.delete(0, tk.END); self.ent_std_age.delete(0, tk.END); self.ent_std_email.delete(0, tk.END)
            self.ent_std_id.insert(0, values[0]); self.ent_std_name.insert(0, values[1]); self.ent_std_age.insert(0, values[2]); self.ent_std_email.insert(0, values[3])
            self.ent_std_class.set(values[4]); self.selected_old_class = values[4]; self.ent_std_id.config(state="readonly")

    def upload_csv(self):
        filepath = filedialog.askopenfilename(title="Select Student CSV", filetypes=(("CSV files", "*.csv"), ("All files", "*.*")))
        if filepath:
            success, msg = self.controller.school.admin.upload_student_csv(filepath)
            messagebox.showinfo("Success", msg) if success else messagebox.showerror("Error", msg); self.refresh_student_table()

    def add_std(self):
        if not all([self.ent_std_name.get(), self.ent_std_age.get(), self.ent_std_email.get(), self.ent_std_class.get()]): return messagebox.showwarning("Warning", "All fields required!")
        if not self.ent_std_age.get().isdigit(): return messagebox.showwarning("Warning", "Age must be a number!")
        success, msg = self.controller.school.admin.add_single_student(self.ent_std_name.get(), self.ent_std_age.get(), self.ent_std_email.get(), self.ent_std_class.get())
        messagebox.showinfo("Success", msg); self.refresh_student_table()

    def add_class_to_std(self):
        if not self.ent_std_id.get(): return messagebox.showwarning("Warning", "Select an existing student first!")
        success, msg = self.controller.school.admin.add_class_to_student(self.ent_std_id.get(), self.ent_std_name.get(), self.ent_std_age.get(), self.ent_std_email.get(), self.ent_std_class.get())
        if success: messagebox.showinfo("Success", msg); self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def update_std(self):
        if not self.ent_std_id.get(): return messagebox.showwarning("Warning", "Select a student first!")
        success, msg = self.controller.school.admin.update_student(self.ent_std_id.get(), self.ent_std_name.get(), self.ent_std_age.get(), self.ent_std_email.get(), self.selected_old_class, self.ent_std_class.get())
        if success: messagebox.showinfo("Success", msg); self.selected_old_class = self.ent_std_class.get(); self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def remove_std(self):
        if not self.ent_std_id.get(): return messagebox.showwarning("Warning", "Select a student first!")
        success, msg = self.controller.school.admin.remove_student_class(self.ent_std_id.get(), self.selected_old_class)
        if success: messagebox.showinfo("Success", msg); self.ent_std_id.config(state="normal"); self.ent_std_id.delete(0, tk.END); self.ent_std_id.config(state="readonly"); self.refresh_student_table()
        else: messagebox.showerror("Error", msg)

    def setup_class_tab(self):
        form_frame = tk.Frame(self.tab_class); form_frame.pack(fill="x", pady=20, padx=10)
        tk.Label(form_frame, text="Select Class:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.cmb_assign_class = ttk.Combobox(form_frame, values=["BIC3104 Programming for Computer Science", "BIC3133 Object Oriented Methods", "BIC3223 Network Security Design", "BIC3253 Entrepreneurship", "BIC2283 Business Systems Development Tools", "BIC3163 Application Layer Programming"], width=45, state="readonly"); self.cmb_assign_class.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        tk.Label(form_frame, text="Select Lecturer:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.cmb_assign_lec = ttk.Combobox(form_frame, width=45, state="readonly"); self.cmb_assign_lec.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        tk.Label(form_frame, text="Day:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.cmb_day = ttk.Combobox(form_frame, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], width=20, state="readonly"); self.cmb_day.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        time_vals = [f"{h}:{m:02d}" for h in range(1, 13) for m in (0, 30)]
        tk.Label(form_frame, text="Start Time:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        start_frame = tk.Frame(form_frame); start_frame.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        self.cmb_start_time = ttk.Combobox(start_frame, values=time_vals, width=8, state="readonly"); self.cmb_start_time.pack(side="left", padx=(0, 5))
        self.cmb_start_ampm = ttk.Combobox(start_frame, values=["AM", "PM"], width=5, state="readonly"); self.cmb_start_ampm.pack(side="left")
        tk.Label(form_frame, text="End Time:").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        end_frame = tk.Frame(form_frame); end_frame.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        self.cmb_end_time = ttk.Combobox(end_frame, values=time_vals, width=8, state="readonly"); self.cmb_end_time.pack(side="left", padx=(0, 5))
        self.cmb_end_ampm = ttk.Combobox(end_frame, values=["AM", "PM"], width=5, state="readonly"); self.cmb_end_ampm.pack(side="left")
        btn_frame = tk.Frame(self.tab_class); btn_frame.pack(fill="x", pady=5, padx=10)
        tk.Button(btn_frame, text="Assign Schedule", bg="#4CAF50", fg="white", command=self.assign_lec).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Remove Schedule", bg="#f44336", fg="white", command=self.remove_assign).pack(side="left", padx=5)
        
        self.tree_class = ttk.Treeview(self.tab_class, columns=("Class Name", "Lecturer ID", "Lecturer Name", "Day", "Start Time", "End Time"), show="headings")
        for col in ("Class Name", "Lecturer ID", "Lecturer Name", "Day", "Start Time", "End Time"): self.tree_class.heading(col, text=col)
        self.tree_class.column("Lecturer ID", width=80); self.tree_class.column("Day", width=80); self.tree_class.column("Start Time", width=80); self.tree_class.column("End Time", width=80)
        self.tree_class.pack(fill="both", expand=True, pady=10, padx=10); self.tree_class.bind("<<TreeviewSelect>>", self.on_class_select)

    def refresh_class_table(self):
        for item in self.tree_class.get_children(): self.tree_class.delete(item)
        for _, row in self.controller.school.admin.get_all_assignments().iterrows():
            self.tree_class.insert("", "end", values=(row.get('Class Name', ''), row.get('Lecturer ID', ''), row.get('Lecturer Name', ''), row.get('Day', ''), row.get('Start Time', ''), row.get('End Time', '')))
        lecturers = self.controller.school.admin.get_all_employees()
        lecturers = lecturers[lecturers['Position'] == 'Lecturer']
        self.cmb_assign_lec['values'] = [f"{row['ID']} - {row['Name']}" for _, row in lecturers.iterrows()]

    def on_class_select(self, event):
        selected = self.tree_class.selection()
        if not selected: return
        values = self.tree_class.item(selected[0], 'values')
        if values:
            self.cmb_assign_class.set(values[0]); self.cmb_assign_lec.set(f"{values[1]} - {values[2]}"); self.cmb_day.set(values[3])
            if values[4] and len(values[4].split(" ")) == 2: self.cmb_start_time.set(values[4].split(" ")[0]); self.cmb_start_ampm.set(values[4].split(" ")[1])
            if values[5] and len(values[5].split(" ")) == 2: self.cmb_end_time.set(values[5].split(" ")[0]); self.cmb_end_ampm.set(values[5].split(" ")[1])

    def assign_lec(self):
        if not all([self.cmb_assign_class.get(), self.cmb_assign_lec.get(), self.cmb_day.get(), self.cmb_start_time.get(), self.cmb_start_ampm.get(), self.cmb_end_time.get(), self.cmb_end_ampm.get()]):
            return messagebox.showwarning("Warning", "Please completely fill out the schedule and assignment!")
        lec_id, lec_name = self.cmb_assign_lec.get().split(" - ", 1)
        success, msg = self.controller.school.admin.assign_lecturer(self.cmb_assign_class.get(), lec_id, lec_name, self.cmb_day.get(), f"{self.cmb_start_time.get()} {self.cmb_start_ampm.get()}", f"{self.cmb_end_time.get()} {self.cmb_end_ampm.get()}")
        if success: messagebox.showinfo("Success", msg); self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def remove_assign(self):
        class_name = self.cmb_assign_class.get()
        day = self.cmb_day.get()
        start_time = f"{self.cmb_start_time.get()} {self.cmb_start_ampm.get()}"
        
        if not class_name or not day or not self.cmb_start_time.get(): 
            return messagebox.showwarning("Warning", "Select a specific schedule from the list to remove first!")
            
        success, msg = self.controller.school.admin.remove_assignment(class_name, day, start_time)
        if success: 
            messagebox.showinfo("Success", msg)
            self.cmb_assign_class.set(""); self.cmb_assign_lec.set(""); self.cmb_day.set("")
            self.cmb_start_time.set(""); self.cmb_start_ampm.set(""); self.cmb_end_time.set(""); self.cmb_end_ampm.set("")
            self.refresh_class_table()
        else: messagebox.showerror("Error", msg)

    def setup_analytics_tab(self):
        form_frame = tk.Frame(self.tab_analytics); form_frame.pack(fill="x", pady=20, padx=10)
        tk.Label(form_frame, text="Select Class for Report:").grid(row=0, column=0, padx=5, pady=5)
        self.cmb_report_class = ttk.Combobox(form_frame, values=["BIC3104 Programming for Computer Science", "BIC3133 Object Oriented Methods", "BIC3223 Network Security Design", "BIC3253 Entrepreneurship", "BIC2283 Business Systems Development Tools", "BIC3163 Application Layer Programming"], width=45, state="readonly"); self.cmb_report_class.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(form_frame, text="Generate NumPy Report", bg="#9C27B0", fg="white", command=self.generate_report).grid(row=0, column=2, padx=15, pady=5)
        self.report_display = tk.Text(self.tab_analytics, height=18, width=70, font=("Courier", 11), bg="#f4f4f4"); self.report_display.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.cmb_report_class.bind("<<ComboboxSelected>>", lambda event: self.generate_report())

    def generate_report(self):
        class_name = self.cmb_report_class.get()
        if not class_name: return messagebox.showwarning("Warning", "Select a class first!")
        success, data = self.controller.school.admin.get_class_analytics(class_name)
        self.report_display.delete(1.0, tk.END)
        if success:
            report_text = f"==========================================================\n            NUMPY STATISTICAL CLASS INSIGHTS\n==========================================================\n\n"
            report_text += f" CLASS: {class_name}\n ENROLLMENT: {data['total_students']} Students\n GRADED: {data['graded_students']} Students\n --------------------------------------------------------\n\n"
            report_text += f" ATTENDANCE TRENDS (NumPy Analysis):\n   - Average Class Attendance: {data['avg_attendance']}%\n   - Highest Attendance:       {data['max_attendance']}%\n   - Lowest Attendance:        {data['min_attendance']}%\n\n"
            report_text += f" PERFORMANCE TRENDS (NumPy Analysis):\n   - Class Average GPA:        {data['avg_gpa']} / 4.0\n   - Class Pass Rate:          {data['pass_rate']}% (Grade C or higher)\n==========================================================\n"
            self.report_display.insert(tk.END, report_text)
        else: self.report_display.insert(tk.END, f"Error Generating Report:\n{data}")

# --- Lecturer Dashboard ---
class LecturerDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.assigned_classes = [] 
        
        header_frame = tk.Frame(self, bg="#2196F3", height=50); header_frame.pack(fill="x")
        self.lbl_welcome = tk.Label(header_frame, text="Lecturer Dashboard", fg="white", bg="#2196F3", font=("Arial", 16, "bold")); self.lbl_welcome.pack(side="left", padx=10, pady=10)
        tk.Button(header_frame, text="Logout", command=lambda: controller.show_frame("LoginFrame")).pack(side="right", padx=10)
        
        self.notebook = ttk.Notebook(self); self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_schedule = tk.Frame(self.notebook); self.notebook.add(self.tab_schedule, text="My Schedule"); self.setup_schedule_tab()
        self.tab_students = tk.Frame(self.notebook); self.notebook.add(self.tab_students, text="Grading & Attendance"); self.setup_students_tab()

    def setup_lecturer_data(self):
        self.lbl_welcome.config(text=f"Lecturer Dashboard - ID: {self.controller.current_user_id}")
        self.refresh_schedule_table()
        
        df_classes = self.controller.school.admin.get_all_assignments()
        my_classes = df_classes[df_classes['Lecturer ID'].astype(str) == str(self.controller.current_user_id)]
        
        self.assigned_classes = my_classes['Class Name'].drop_duplicates().tolist()
        self.cmb_filter_class['values'] = self.assigned_classes
        if self.assigned_classes:
            self.cmb_filter_class.set(self.assigned_classes[0]); self.refresh_roster()

    def setup_schedule_tab(self):
        tk.Label(self.tab_schedule, text="Your Assigned Classes", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.tree_sched = ttk.Treeview(self.tab_schedule, columns=("Class Name", "Day", "Start Time", "End Time"), show="headings")
        for col in ("Class Name", "Day", "Start Time", "End Time"): self.tree_sched.heading(col, text=col)
        self.tree_sched.pack(fill="both", expand=True, pady=10, padx=10)

    def refresh_schedule_table(self):
        for item in self.tree_sched.get_children(): self.tree_sched.delete(item)
        df = self.controller.school.admin.get_all_assignments()
        my_schedule = df[df['Lecturer ID'].astype(str) == str(self.controller.current_user_id)]
        for _, row in my_schedule.iterrows(): self.tree_sched.insert("", "end", values=(row['Class Name'], row['Day'], row['Start Time'], row['End Time']))

    def setup_students_tab(self):
        top_frame = tk.Frame(self.tab_students); top_frame.pack(fill="x", pady=10, padx=10)
        tk.Label(top_frame, text="Select Class:").pack(side="left", padx=5)
        self.cmb_filter_class = ttk.Combobox(top_frame, width=45, state="readonly"); self.cmb_filter_class.pack(side="left", padx=5)
        tk.Button(top_frame, text="Load Roster", command=self.refresh_roster, bg="#607D8B", fg="white").pack(side="left", padx=10)
        tk.Button(top_frame, text="Take Daily Attendance \u2714", command=self.open_attendance_popup, bg="#FF9800", fg="black", font=("Arial", 9, "bold")).pack(side="right", padx=10)
        
        form_frame = tk.Frame(self.tab_students, bd=1, relief="solid", bg="#f9f9f9"); form_frame.pack(fill="x", pady=10, padx=10)
        
        tk.Label(form_frame, text="Student ID:", bg="#f9f9f9").grid(row=0, column=0, padx=5, pady=10)
        self.ent_grade_id = tk.Entry(form_frame, width=10, state="readonly"); self.ent_grade_id.grid(row=0, column=1, padx=5, pady=10)
        tk.Label(form_frame, text="Name:", bg="#f9f9f9").grid(row=0, column=2, padx=5, pady=10)
        self.ent_grade_name = tk.Entry(form_frame, width=20, state="readonly"); self.ent_grade_name.grid(row=0, column=3, padx=5, pady=10)
        tk.Label(form_frame, text="Score (0-100):", bg="#f9f9f9").grid(row=0, column=4, padx=5, pady=10)
        self.ent_score = tk.Entry(form_frame, width=8); self.ent_score.grid(row=0, column=5, padx=5, pady=10)
        tk.Button(form_frame, text="Save Score", bg="#4CAF50", fg="white", command=self.save_marks).grid(row=0, column=6, padx=15, pady=10)
        
        self.tree_roster = ttk.Treeview(self.tab_students, columns=("ID", "Name", "Score", "Grade", "Attended/Total", "Attendance %"), show="headings")
        for col in ("ID", "Name", "Score", "Grade", "Attended/Total", "Attendance %"): self.tree_roster.heading(col, text=col)
        self.tree_roster.column("ID", width=50); self.tree_roster.column("Score", width=60); self.tree_roster.column("Grade", width=60)
        self.tree_roster.pack(fill="both", expand=True, pady=10, padx=10); self.tree_roster.bind("<<TreeviewSelect>>", self.on_roster_select)

    def refresh_roster(self):
        for item in self.tree_roster.get_children(): self.tree_roster.delete(item)
        if not self.cmb_filter_class.get(): return
        class_roster = self.controller.school.admin.get_all_students()
        class_roster = class_roster[class_roster['Class'] == self.cmb_filter_class.get()]
        
        for _, row in class_roster.iterrows(): 
            attended_str = f"{row.get('Attended', 0)} / {row.get('Total Classes', 0)}"
            self.tree_roster.insert("", "end", values=(row['ID'], row['Name'], row.get('Score', '0'), row.get('Grade', 'N/A'), attended_str, row.get('Attendance', '0%')))

    def on_roster_select(self, event):
        selected = self.tree_roster.selection()
        if not selected: return
        values = self.tree_roster.item(selected[0], 'values')
        if values:
            self.ent_grade_id.config(state="normal"); self.ent_grade_name.config(state="normal")
            self.ent_grade_id.delete(0, tk.END); self.ent_grade_name.delete(0, tk.END); self.ent_score.delete(0, tk.END)
            self.ent_grade_id.insert(0, values[0]); self.ent_grade_name.insert(0, values[1]); self.ent_score.insert(0, values[2])
            self.ent_grade_id.config(state="readonly"); self.ent_grade_name.config(state="readonly")

    def save_marks(self):
        if not self.ent_grade_id.get(): return messagebox.showwarning("Warning", "Select a student from the roster first!")
        score_val = self.ent_score.get()
        if not score_val.replace('.', '', 1).isdigit(): return messagebox.showwarning("Warning", "Score must be a number!")
            
        success, msg = self.controller.school.teacher.update_student_score(self.ent_grade_id.get(), self.cmb_filter_class.get(), score_val)
        if success: messagebox.showinfo("Success", msg); self.refresh_roster()
        else: messagebox.showerror("Error", msg)
            
    def open_attendance_popup(self):
        active_class = self.cmb_filter_class.get()
        if not active_class: return messagebox.showwarning("Warning", "Select a class from the dropdown first!")
            
        df = self.controller.school.admin.get_all_students()
        roster = df[df['Class'] == active_class]
        if roster.empty: return messagebox.showinfo("Info", "No students are currently enrolled in this class.")
            
        popup = tk.Toplevel(self)
        popup.title(f"Take Attendance: {active_class}")
        popup.geometry("450x600")
        tk.Label(popup, text=f"Today's Attendance for:\n{active_class}", font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(popup, text="Check the box if the student is PRESENT:", fg="gray").pack(pady=(0, 10))
        
        scroll_frame = tk.Frame(popup); scroll_frame.pack(fill="both", expand=True, padx=20)
        self.attendance_vars = {}
        
        for _, row in roster.iterrows():
            var = tk.IntVar(value=1) 
            chk = tk.Checkbutton(scroll_frame, text=f"ID: {row['ID']} - {row['Name']}", variable=var, font=("Arial", 10))
            chk.pack(anchor="w", pady=2)
            self.attendance_vars[row['ID']] = var
            
        tk.Button(popup, text="Save Attendance List", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), command=lambda: self.save_attendance_batch(active_class, popup)).pack(pady=20)

    def save_attendance_batch(self, class_name, popup):
        present_ids = [std_id for std_id, var in self.attendance_vars.items() if var.get() == 1]
        success, msg = self.controller.school.teacher.record_daily_attendance(class_name, present_ids)
        if success: messagebox.showinfo("Success", msg); popup.destroy(); self.refresh_roster()
        else: messagebox.showerror("Error", msg)

# ==========================================
# 4. RUN APPLICATION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()