# ==========================================
# BASE CLASS
# ==========================================
class Person:
    def __init__(self, person_id=None, name=None, contact=None, email=None):
        self.id = person_id
        self.name = name
        self.contact = contact
        self.email = email
