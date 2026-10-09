from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    """
    Abstract Base Class for all domain entities in DevTrack.
    Enforces validation and dictionary serialization contracts.
    """

    @abstractmethod
    def validate(self):
        """Must be implemented by subclasses to enforce domain validation rules."""
        pass

    def to_dict(self):
        """Converts object instance attributes into a dictionary representation."""
        return {key: value for key, value in self.__dict__.items()}


class Reporter(BaseEntity):
    """
    Represents a person/engineer who files issues.
    """

    def __init__(self, id, name, email, team):
        self.id = int(id) if id is not None else None
        self.name = name
        self.email = email
        self.team = team

    def validate(self):
        """Validates reporter fields."""
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email")


class Issue(BaseEntity):
    """
    Base class representing a bug report or task filed by a Reporter.
    """

    ALLOWED_STATUSES = ["open", "in_progress", "resolved", "closed"]
    ALLOWED_PRIORITIES = ["low", "medium", "high", "critical"]

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = int(id) if id is not None else None
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.reporter_id = int(reporter_id) if reporter_id is not None else None
        self.created_at = created_at if created_at is not None else str(datetime.now())

    def validate(self):
        """Validates issue attributes against business constraints."""
        if not self.title:
            raise ValueError("Title cannot be empty")
        if self.status not in self.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status. Allowed values: {', '.join(self.ALLOWED_STATUSES)}")
        if self.priority not in self.ALLOWED_PRIORITIES:
            raise ValueError(f"Invalid priority. Allowed values: {', '.join(self.ALLOWED_PRIORITIES)}")

    def describe(self):
        """Returns a string description of the issue (default format for medium/high priority)."""
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    """
    Subclass for critical priority issues overriding describe().
    """

    def describe(self):
        return f"[URGENT] {self.title} — needs immediate attention"


class LowPriorityIssue(Issue):
    """
    Subclass for low priority issues overriding describe().
    """

    def describe(self):
        return f"{self.title} — low priority, handle when free"
