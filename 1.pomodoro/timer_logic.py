"""
Timer Logic Module - Pure Business Logic for Pomodoro Timer

This module contains the core business logic for the Pomodoro timer:
- PomodoroSession: Manages timer state and calculations
- WorkSessionTracker: Tracks session statistics
"""

from datetime import datetime, date


class PomodoroSession:
    """
    Manages a single Pomodoro session with pure calculation logic.
    
    No side effects - all methods are predictable and testable.
    """

    def __init__(self, work_minutes=25, break_minutes=5):
        """
        Initialize a Pomodoro session.
        
        Args:
            work_minutes (int): Duration of work session in minutes (default: 25)
            break_minutes (int): Duration of break session in minutes (default: 5)
        """
        self.work_seconds = work_minutes * 60
        self.break_seconds = break_minutes * 60
        self.elapsed_seconds = 0

    def tick(self):
        """
        Increment elapsed time by 1 second.
        Called once per second during active timer.
        """
        self.elapsed_seconds += 1

    def get_remaining(self):
        """
        Get remaining time in seconds (pure function, no side effects).
        
        Returns:
            int: Remaining seconds, never negative
        """
        return max(0, self.work_seconds - self.elapsed_seconds)

    def is_complete(self):
        """
        Check if the session is complete.
        
        Returns:
            bool: True if elapsed time >= work time
        """
        return self.elapsed_seconds >= self.work_seconds

    def get_progress_ratio(self):
        """
        Calculate progress as ratio between 0 and 1.
        
        Returns:
            float: Progress ratio (0.0 = start, 1.0 = complete)
        """
        if self.work_seconds == 0:
            return 0.0
        return min(1.0, self.elapsed_seconds / self.work_seconds)

    def reset(self):
        """Reset timer to initial state (elapsed_seconds = 0)."""
        self.elapsed_seconds = 0

    def format_time(self):
        """
        Format remaining time as MM:SS string.
        
        Returns:
            str: Formatted time (e.g., "24:59")
        """
        seconds = self.get_remaining()
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def get_elapsed_seconds(self):
        """Get total elapsed seconds in this session."""
        return self.elapsed_seconds

    def set_elapsed_seconds(self, seconds):
        """Set elapsed seconds (for testing and recovery scenarios)."""
        self.elapsed_seconds = max(0, seconds)


class WorkSessionTracker:
    """
    Track Pomodoro session statistics.
    
    Manages:
    - Count of completed sessions today
    - Total minutes focused today
    - Date-based reset logic
    """

    def __init__(self):
        """Initialize session tracker."""
        self.sessions_completed = 0
        self.total_minutes = 0
        self.date = date.today()

    def add_completed_session(self, minutes):
        """
        Record a completed session.
        
        Args:
            minutes (int): Duration of completed session in minutes
        """
        self.sessions_completed += 1
        self.total_minutes += minutes

    def get_stats_dict(self):
        """
        Get statistics as dictionary.
        
        Returns:
            dict: Statistics with keys 'completed', 'totalMinutes', 'date'
        """
        return {
            'completed': self.sessions_completed,
            'totalMinutes': self.total_minutes,
            'date': self.date.isoformat()
        }

    def is_same_day(self, check_date=None):
        """
        Check if given date is same as tracker date.
        
        Args:
            check_date (date, optional): Date to check (default: today)
            
        Returns:
            bool: True if same day
        """
        if check_date is None:
            check_date = date.today()
        return self.date == check_date

    def reset_if_new_day(self):
        """
        Reset statistics if date has changed.
        
        Returns:
            bool: True if reset occurred
        """
        today = date.today()
        if today != self.date:
            self.sessions_completed = 0
            self.total_minutes = 0
            self.date = today
            return True
        return False

    def get_hours_minutes_str(self):
        """
        Get total time as human-readable string.
        
        Returns:
            str: Format like "1時間40分" or "20分"
        """
        hours = self.total_minutes // 60
        minutes = self.total_minutes % 60
        
        if hours == 0:
            return f"{minutes}分"
        return f"{hours}時間{minutes}分"
