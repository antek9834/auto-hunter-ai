"""
SLA (Service Level Agreement) Calculator
Calculates deadline based on ticket urgency.
"""
from datetime import datetime, timedelta
from langfuse import observe


class SLACalculator:
    """Calculate SLA deadlines for support tickets."""

    # SLA response times by urgency level
    SLA_HOURS = {
        "critical": 4,    # 4 hours for critical issues
        "high": 24,       # 1 day for high priority
        "medium": 48,     # 2 days for medium priority
        "low": 72         # 3 days for low priority
    }

    @observe(as_type="tool")
    def calculate_deadline(self, urgency: str, created_at: str = None) -> str:
        """
        Calculate SLA deadline based on urgency level.

        Args:
            urgency: Ticket urgency ('critical', 'high', 'medium', 'low')
            created_at: ISO format datetime string (defaults to now)

        Returns:
            ISO format datetime string of deadline

        Examples:
            >>> calc = SLACalculator()
            >>> calc.calculate_deadline("critical")
            '2024-11-20T14:30:00'
        """
        urgency = urgency.lower()

        if urgency not in self.SLA_HOURS:
            # Default to medium if urgency not recognized
            urgency = "medium"

        # Start time
        if created_at:
            start = datetime.fromisoformat(created_at)
        else:
            start = datetime.now()

        # Add SLA hours
        hours_to_add = self.SLA_HOURS[urgency]
        deadline = start + timedelta(hours=hours_to_add)

        return deadline.isoformat()

    @observe(as_type="tool")
    def hours_remaining(self, deadline: str) -> float:
        """
        Calculate hours remaining until deadline.

        Args:
            deadline: ISO format datetime string

        Returns:
            Hours remaining (negative if overdue)
        """
        deadline_dt = datetime.fromisoformat(deadline)
        delta = deadline_dt - datetime.now()
        return delta.total_seconds() / 3600
