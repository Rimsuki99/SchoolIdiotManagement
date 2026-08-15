import pandas as pd
import numpy as np
import os

from person import Person

# ==========================================
# ADMIN: Employee, Student & Class/Schedule Management
# ==========================================
class Admin(Person):
    def __init__(self, person_id=None, name=None, contact=None, email=None):
        super().__init__(person_id, name, contact, email)
        self.emp_file = 'employees.csv'
        self.std_file = 'students.csv'
        self.cls_file = 'classes.csv'

        if not os.path.exists(self.emp_file):
            pd.DataFrame(columns=['ID', 'Name', 'Contact', 'Email', 'Position']).to_csv(self.emp_file, index=False)

        if not os.path.exists(self.std_file):
            pd.DataFrame(columns=['ID', 'Name', 'Age', 'Email', 'Class', 'Score', 'Grade', 'Attended', 'Total Classes', 'Attendance']).to_csv(self.std_file, index=False)
        else:
            df = pd.read_csv(self.std_file)
            changed = False
            new_cols = {'Score': '0', 'Grade': 'N/A', 'Attended': 0, 'Total Classes': 0, 'Attendance': '0%'}
            for col, default_val in new_cols.items():
                if col not in df.columns:
                    df[col] = default_val
                    changed = True
            if changed:
                df.to_csv(self.std_file, index=False)

        if not os.path.exists(self.cls_file):
            pd.DataFrame(columns=['Class Name', 'Lecturer ID', 'Lecturer Name', 'Day', 'Start Time', 'End Time']).to_csv(self.cls_file, index=False)

    # --- Employee Management ---
    def get_all_employees(self):
        return pd.read_csv(self.emp_file)

    def generate_emp_id(self, position):
        df = pd.read_csv(self.emp_file)
        pos_df = df[df['Position'] == position]
        if pos_df.empty: return 2001 if position == "Lecturer" else 3001
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
        if emp_id not in df['ID'].values: return False, "Employee ID not found."
        df = df[df['ID'] != emp_id]
        df.to_csv(self.emp_file, index=False)
        return True, "Employee Removed!"

    def update_employee(self, emp_id, name, contact, email, position):
        df = pd.read_csv(self.emp_file)
        emp_id = int(emp_id)
        df['Name'] = df['Name'].astype(str); df['Contact'] = df['Contact'].astype(str)
        df['Email'] = df['Email'].astype(str); df['Position'] = df['Position'].astype(str)
        if emp_id not in df['ID'].values: return False, "Employee ID not found."
        df.loc[df['ID'] == emp_id, ['Name', 'Contact', 'Email', 'Position']] = [name, contact, email, position]
        df.to_csv(self.emp_file, index=False)
        return True, "Employee Updated!"

    # --- Student Management ---
    def get_all_students(self):
        return pd.read_csv(self.std_file)

    def generate_std_id(self):
        df = pd.read_csv(self.std_file)
        if df.empty: return 4001
        return int(df['ID'].max()) + 1

    def add_single_student(self, name, age, email, std_class):
        df = pd.read_csv(self.std_file)
        new_id = self.generate_std_id()
        new_std = pd.DataFrame([{'ID': new_id, 'Name': name, 'Age': age, 'Email': email, 'Class': std_class, 'Score': '0', 'Grade': 'N/A', 'Attended': 0, 'Total Classes': 0, 'Attendance': '0%'}])
        df = pd.concat([df, new_std], ignore_index=True)
        df.to_csv(self.std_file, index=False)
        return True, f"New Student Added!\nAuto-Assigned ID: {new_id}"

    def add_class_to_student(self, std_id, name, age, email, new_class):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)
        if not df[(df['ID'] == std_id) & (df['Class'] == new_class)].empty:
            return False, f"Student is already enrolled in {new_class}!"
        new_row = pd.DataFrame([{'ID': std_id, 'Name': name, 'Age': age, 'Email': email, 'Class': new_class, 'Score': '0', 'Grade': 'N/A', 'Attended': 0, 'Total Classes': 0, 'Attendance': '0%'}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(self.std_file, index=False)
        return True, f"Class {new_class} added to Student {std_id}!"

    def upload_student_csv(self, filepath):
        try:
            new_df = pd.read_csv(filepath)
            required_columns = ['Name', 'Age', 'Email', 'Class']
            if not all(col in new_df.columns for col in required_columns): return False, "CSV must contain columns: Name, Age, Email, Class"

            df = pd.read_csv(self.std_file)
            if 'ID' in new_df.columns: new_df = new_df.drop(columns=['ID'])

            added_count = 0
            for index, row in new_df.iterrows():
                name = str(row['Name']).strip(); email = str(row['Email']).strip()
                age = str(row['Age']).strip(); std_class = str(row['Class']).strip()

                if not df[(df['Email'] == email) & (df['Class'] == std_class)].empty: continue

                existing_student = df[df['Email'] == email]
                if not existing_student.empty: std_id = existing_student.iloc[0]['ID']
                else: std_id = 4001 if df.empty else int(df['ID'].max()) + 1

                new_row = pd.DataFrame([{'ID': std_id, 'Name': name, 'Age': age, 'Email': email, 'Class': std_class, 'Score': '0', 'Grade': 'N/A', 'Attended': 0, 'Total Classes': 0, 'Attendance': '0%'}])
                df = pd.concat([df, new_row], ignore_index=True)
                added_count += 1

            df.to_csv(self.std_file, index=False)
            if added_count == 0: return True, "No new records added."
            else: return True, f"Successfully imported {added_count} new student records!"
        except Exception as e:
            return False, f"Error processing file: {str(e)}"

    def update_student(self, std_id, name, age, email, old_class, new_class):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)
        df['Name'] = df['Name'].astype(str); df['Email'] = df['Email'].astype(str); df['Class'] = df['Class'].astype(str)
        if std_id not in df['ID'].values: return False, "Student ID not found."

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

    # --- Class & Schedule Management ---
    def get_all_assignments(self):
        return pd.read_csv(self.cls_file)

    def assign_lecturer(self, class_name, lec_id, lec_name, day, start_time, end_time):
        df = pd.read_csv(self.cls_file)
        for col in ['Lecturer ID', 'Lecturer Name', 'Day', 'Start Time', 'End Time']:
            if col in df.columns: df[col] = df[col].astype(str)

        mask = (df['Class Name'] == class_name) & (df['Day'] == day) & (df['Start Time'] == start_time)

        if not df[mask].empty:
            df.loc[mask, ['Lecturer ID', 'Lecturer Name', 'End Time']] = [str(lec_id), lec_name, end_time]
            msg = "Existing schedule block updated!"
        else:
            new_row = pd.DataFrame([{'Class Name': class_name, 'Lecturer ID': str(lec_id), 'Lecturer Name': lec_name, 'Day': day, 'Start Time': start_time, 'End Time': end_time}])
            df = pd.concat([df, new_row], ignore_index=True)
            msg = "New schedule block successfully assigned!"

        df.to_csv(self.cls_file, index=False)
        return True, msg

    def remove_assignment(self, class_name, day, start_time):
        df = pd.read_csv(self.cls_file)
        mask = (df['Class Name'] == class_name) & (df['Day'] == day) & (df['Start Time'] == start_time)

        if df[mask].empty:
            return False, "No assignment found for this specific schedule block."

        df = df[~mask]
        df.to_csv(self.cls_file, index=False)
        return True, "Schedule block removed!"

    # --- Reporting & Statistical Insights ---
    def get_class_analytics(self, class_name):
        df = pd.read_csv(self.std_file)
        df['Class'] = df['Class'].astype(str).str.strip()
        class_name = class_name.strip()

        class_df = df[df['Class'] == class_name]
        if class_df.empty: return False, "No students are currently enrolled in this class."

        attendances = class_df['Attendance'].astype(str).str.replace('%', '')
        attendances = pd.to_numeric(attendances, errors='coerce').fillna(0).to_numpy()
        avg_att = np.mean(attendances); max_att = np.max(attendances); min_att = np.min(attendances)

        grade_map = {"A": 4.0, "A-": 3.67, "B+": 3.33, "B": 3.0, "B-": 2.67, "C+": 2.33, "C": 2.0, "D": 1.0, "F": 0.0, "N/A": np.nan}
        clean_grades = class_df['Grade'].astype(str).str.strip().str.upper()
        numeric_grades = clean_grades.map(grade_map).to_numpy()
        valid_grades = numeric_grades[~np.isnan(numeric_grades)]

        if len(valid_grades) > 0:
            avg_gpa = np.mean(valid_grades)
            pass_rate = np.mean(valid_grades >= 2.0) * 100
        else:
            avg_gpa = 0.0; pass_rate = 0.0

        report_data = {
            "total_students": len(class_df), "graded_students": len(valid_grades),
            "avg_attendance": round(avg_att, 2), "max_attendance": round(max_att, 2), "min_attendance": round(min_att, 2),
            "avg_gpa": round(avg_gpa, 2), "pass_rate": round(pass_rate, 2)
        }
        return True, report_data
