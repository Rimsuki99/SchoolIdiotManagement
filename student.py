from person import Person

# ==========================================
# STUDENT: Stores student details and academic records
# ==========================================
class Student(Person):
    def __init__(self, student_id=None, name=None, age=None, email=None, student_class=None,
                 score='0', grade='N/A', attended=0, total_classes=0, attendance='0%'):
        super().__init__(student_id, name, email=email)
        self.age = age
        self.student_class = student_class
        self.score = score
        self.grade = grade
        self.attended = attended
        self.total_classes = total_classes
        self.attendance = attendance
