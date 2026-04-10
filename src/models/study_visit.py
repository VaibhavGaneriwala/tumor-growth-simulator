# Author: Vaibhav Ganeriwala
# Description: StudyVisit class for Tumor Growth Simulator

from dataclasses import dataclass
from datetime import datetime

@dataclass
class StudyVisit:
    """A single imaging visit with optional paths to MRI files."""
    study_datetime: datetime
    age_at_study: int = None
    pre_path: str = None
    post_path: str = None
    t2_path: str = None
    flair_path: str = None

    def has_any_image(self):
        """True if at least one MRI sequence file is attached to this visit."""
        return any([self.pre_path, self.post_path, self.t2_path, self.flair_path])