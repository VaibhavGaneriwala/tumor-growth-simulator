# Author: Vaibhav Ganeriwala
# Description: Patient class for Tumor Growth Simulator

from src.models.study_visit import StudyVisit

class Patient:
    """
    Represents a patient in the tumor growth simulator.
    """
    
    def __init__(self, patient_id, sex=None, visits=None):
        self.patient_id = patient_id
        self.sex = sex
        self.visits = list(visits) if visits else []

    def add_visit(self, visit):
        """Append a StudyVisit to this patient's timeline."""
        self.visits.append(visit)

    def num_visits(self):
        """Return how many imaging visits this patient has."""
        return len(self.visits)

    def get_visits_sorted(self):
        """Return visits ordered by study_datetime (earliest first)."""
        return sorted(self.visits, key=lambda v: v.study_datetime)
    
    def first_visit_date(self):
        """Datetime of the earliest visit, or None if no visits yet."""
        if not self.visits:
            return None
        return min(v.study_datetime for v in self.visits)
    
    def latest_visit_date(self):
        """Datetime of the most recent visit, or None if no visits yet."""
        if not self.visits:
            return None
        return max(v.study_datetime for v in self.visits)
    
    def age_range(self):
        """
        Return (min_age, max_age) across all visits with a known age.
        Return None if no visit has a usage age value.
        """
        ages = [v.age_at_study for v in self.visits if v.age_at_study is not None]
        if not ages:
            return None
        return (min(ages), max(ages))
    
    def __repr__(self):
        return (
            f"Patient(id={self.patient_id!r}, sex={self.sex!r}, "
            f"visits={self.num_visits()})"
        )