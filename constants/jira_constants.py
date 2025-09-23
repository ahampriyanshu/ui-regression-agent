"""
JIRA-related constants for UI Regression Testing

Contains all valid values for JIRA ticket fields including status, type,
priority, and user assignments.
"""

from enum import Enum
from typing import List


class TicketStatus(Enum):
    """Valid ticket statuses"""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    ON_HOLD = "on_hold"
    DONE = "done"


class TicketType(Enum):
    """Valid ticket types"""

    FEATURE = "feature"
    FIX = "fix"
    PERF_IMPROVEMENT = "perf_improvement"


class TicketPriority(Enum):
    """Valid ticket priorities"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Users(Enum):
    """Available users in the system"""

    FRONTEND_DEV = "frontend.dev"
    BACKEND_DEV = "backend.dev"
    PRODUCT_MANAGER = "product.manager"
    PRODUCT_TESTER = "product.tester"
    UI_REGRESSION_AGENT = "ui_regression.agent"


# Convenience lists for validation
VALID_STATUSES: List[str] = [status.value for status in TicketStatus]
VALID_TYPES: List[str] = [ticket_type.value for ticket_type in TicketType]
VALID_PRIORITIES: List[str] = [priority.value for priority in TicketPriority]

# User lists for different roles
VALID_ASSIGNEES: List[str] = [
    Users.FRONTEND_DEV.value,
    Users.BACKEND_DEV.value,
    Users.PRODUCT_TESTER.value,
]

VALID_REPORTERS: List[str] = [
    Users.PRODUCT_MANAGER.value,
    Users.UI_REGRESSION_AGENT.value,
    Users.PRODUCT_TESTER.value,
]
