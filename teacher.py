import pandas as pd

from person import Person

# ==========================================
# TEACHER: Grading & Attendance Management
# ==========================================
class Teacher(Person):
    def __init__(self, person_id=None, name=None, contact=None, email=None):
        super().__init__(person_id, name, contact, email)
        self.std_file = 'students.csv'

    # --- Grading & Assessment ---
    def calculate_grade(self, score_str):
        try:
            score = float(score_str)
            if score >= 80: return "A"
            elif score >= 75: return "A-"
            elif score >= 70: return "B+"
            elif score >= 65: return "B"
            elif score >= 60: return "B-"
            elif score >= 55: return "C+"
            elif score >= 50: return "C"
            elif score >= 40: return "D"
            else: return "F"
        except:
            return "N/A"

    def update_student_score(self, std_id, class_name, score):
        df = pd.read_csv(self.std_file)
        std_id = int(std_id)

        df['Class'] = df['Class'].astype(str)
        df['Score'] = df['Score'].astype(str)
        df['Grade'] = df['Grade'].astype(str)

        mask = (df['ID'] == std_id) & (df['Class'] == class_name)
        if df[mask].empty: return False, "Student not found in this class."

        auto_grade = self.calculate_grade(score)
        df.loc[mask, ['Score', 'Grade']] = [str(score), auto_grade]
        df.to_csv(self.std_file, index=False)
        return True, f"Score saved! Auto-Calculated Grade: {auto_grade}"

    # --- Attendance Management ---
    def record_daily_attendance(self, class_name, present_ids):
        df = pd.read_csv(self.std_file)
        df['Class'] = df['Class'].astype(str)

        df['Total Classes'] = pd.to_numeric(df['Total Classes'], errors='coerce').fillna(0)
        df['Attended'] = pd.to_numeric(df['Attended'], errors='coerce').fillna(0)

        class_mask = df['Class'] == class_name
        df.loc[class_mask, 'Total Classes'] += 1

        for std_id in present_ids:
            mask = (df['ID'] == int(std_id)) & (df['Class'] == class_name)
            df.loc[mask, 'Attended'] += 1

        percentages = (df.loc[class_mask, 'Attended'] / df.loc[class_mask, 'Total Classes'] * 100).round(1)
        df.loc[class_mask, 'Attendance'] = percentages.astype(str) + "%"

        df.to_csv(self.std_file, index=False)
        return True, "Daily attendance recorded successfully!"
