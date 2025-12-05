"""
Business Hours Checker
Determines if current time is within business hours.
"""
from datetime import datetime, time
from langfuse import observe


class BusinessHoursChecker:
    """Check if operations are within business hours."""

    def __init__(
        self,
        start_hour: int = 9,    # 9 AM
        end_hour: int = 17,     # 5 PM
        timezone: str = "UTC"
    ):
        """
        Initialize business hours checker.

        Args:
            start_hour: Business day start hour (24-hour format)
            end_hour: Business day end hour (24-hour format)
            timezone: Timezone string (default UTC)
        """
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.timezone = timezone
        self.business_days = [0, 1, 2, 3, 4]  # Monday=0 to Friday=4

    @observe(as_type="tool")
    def is_business_hours(self, check_time: str = None) -> bool:
        """
        Check if given time is within business hours.

        Args:
            check_time: ISO format datetime string (defaults to now)

        Returns:
            True if within business hours, False otherwise

        Examples:
            >>> checker = BusinessHoursChecker()
            >>> checker.is_business_hours("2024-11-20T14:00:00")  # Wednesday 2 PM
            True
            >>> checker.is_business_hours("2024-11-20T20:00:00")  # Wednesday 8 PM
            False
        """
        if check_time:
            dt = datetime.fromisoformat(check_time)
        else:
            dt = datetime.now()

        # Check if it's a business day (Monday-Friday)
        if dt.weekday() not in self.business_days:
            return False

        # Check if it's within business hours
        current_time = dt.time()
        start_time = time(self.start_hour, 0)
        end_time = time(self.end_hour, 0)

        return start_time <= current_time < end_time

    @observe(as_type="tool")
    def get_status(self, check_time: str = None) -> dict:
        """
        Get detailed business hours status.

        Args:
            check_time: ISO format datetime string (defaults to now)

        Returns:
            Dictionary with status details
        """
        if check_time:
            dt = datetime.fromisoformat(check_time)
        else:
            dt = datetime.now()

        is_business_day = dt.weekday() in self.business_days
        is_business_time = self.is_business_hours(check_time)

        status = {
            "is_business_hours": is_business_time,
            "is_business_day": is_business_day,
            "current_time": dt.isoformat(),
            "day_of_week": dt.strftime("%A"),
            "hour": dt.hour,
            "business_hours_range": f"{self.start_hour}:00 - {self.end_hour}:00"
        }

        if is_business_time:
            status["message"] = "Within business hours - standard response time"
        elif is_business_day:
            status["message"] = "Outside business hours - response may be delayed"
        else:
            status["message"] = "Weekend/holiday - response on next business day"

        return status

