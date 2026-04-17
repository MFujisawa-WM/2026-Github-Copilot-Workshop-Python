"""
Unit Tests for timer_logic.py

Test coverage for:
- PomodoroSession: Time calculations and state management
- WorkSessionTracker: Session statistics and date logic
"""

import pytest
from datetime import date, timedelta
from timer_logic import PomodoroSession, WorkSessionTracker


class TestPomodoroSession:
    """Unit tests for PomodoroSession class."""

    def test_initialization(self):
        """Test session initializes with correct duration."""
        session = PomodoroSession(work_minutes=25, break_minutes=5)
        assert session.work_seconds == 1500  # 25 * 60
        assert session.break_seconds == 300  # 5 * 60
        assert session.elapsed_seconds == 0

    def test_tick_increments_elapsed_time(self):
        """Test tick() increments elapsed seconds."""
        session = PomodoroSession()
        assert session.elapsed_seconds == 0
        session.tick()
        assert session.elapsed_seconds == 1
        session.tick()
        assert session.elapsed_seconds == 2

    def test_get_remaining_at_start(self):
        """Test get_remaining() returns full duration at start."""
        session = PomodoroSession(work_minutes=25)
        assert session.get_remaining() == 1500

    def test_get_remaining_after_ticks(self):
        """Test get_remaining() decreases with ticks."""
        session = PomodoroSession(work_minutes=1)  # 60 seconds
        session.elapsed_seconds = 30
        assert session.get_remaining() == 30

    def test_get_remaining_at_completion(self):
        """Test get_remaining() returns 0 when complete."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 60
        assert session.get_remaining() == 0

    def test_get_remaining_never_negative(self):
        """Test get_remaining() never returns negative."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 120  # Beyond work time
        assert session.get_remaining() == 0

    def test_is_complete_at_start(self):
        """Test is_complete() is False at start."""
        session = PomodoroSession()
        assert session.is_complete() is False

    def test_is_complete_before_end(self):
        """Test is_complete() is False before end time."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 59
        assert session.is_complete() is False

    def test_is_complete_at_end(self):
        """Test is_complete() is True at end time."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 60
        assert session.is_complete() is True

    def test_is_complete_after_end(self):
        """Test is_complete() is True after end time."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 120
        assert session.is_complete() is True

    def test_get_progress_ratio_at_start(self):
        """Test progress ratio at start is 0.0."""
        session = PomodoroSession(work_minutes=25)
        assert session.get_progress_ratio() == 0.0

    def test_get_progress_ratio_midway(self):
        """Test progress ratio at midpoint."""
        session = PomodoroSession(work_minutes=25)
        session.elapsed_seconds = 750  # 12.5 minutes
        assert session.get_progress_ratio() == 0.5

    def test_get_progress_ratio_at_completion(self):
        """Test progress ratio at completion."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 60
        assert session.get_progress_ratio() == 1.0

    def test_get_progress_ratio_never_exceeds_one(self):
        """Test progress ratio never exceeds 1.0."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 120
        assert session.get_progress_ratio() == 1.0

    def test_reset(self):
        """Test reset() clears elapsed time."""
        session = PomodoroSession()
        session.elapsed_seconds = 500
        session.reset()
        assert session.elapsed_seconds == 0
        assert session.get_remaining() == 1500

    def test_format_time_at_start(self):
        """Test format_time() at session start."""
        session = PomodoroSession(work_minutes=25)
        assert session.format_time() == "25:00"

    def test_format_time_single_digit_seconds(self):
        """Test format_time() pads single-digit seconds."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 54  # Remaining: 6 seconds = 00:06
        assert session.format_time() == "00:06"

    def test_format_time_single_digit_minutes(self):
        """Test format_time() pads single-digit minutes."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 30  # Remaining: 30 seconds = 00:30
        assert session.format_time() == "00:30"

    def test_format_time_at_completion(self):
        """Test format_time() at completion."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 60
        assert session.format_time() == "00:00"

    def test_format_time_beyond_completion(self):
        """Test format_time() beyond completion."""
        session = PomodoroSession(work_minutes=1)
        session.elapsed_seconds = 120
        assert session.format_time() == "00:00"

    def test_get_elapsed_seconds(self):
        """Test get_elapsed_seconds() getter."""
        session = PomodoroSession()
        session.elapsed_seconds = 123
        assert session.get_elapsed_seconds() == 123

    def test_set_elapsed_seconds(self):
        """Test set_elapsed_seconds() setter."""
        session = PomodoroSession()
        session.set_elapsed_seconds(500)
        assert session.elapsed_seconds == 500

    def test_set_elapsed_seconds_negative_clamped(self):
        """Test set_elapsed_seconds() clamps negative to 0."""
        session = PomodoroSession()
        session.set_elapsed_seconds(-10)
        assert session.elapsed_seconds == 0


class TestWorkSessionTracker:
    """Unit tests for WorkSessionTracker class."""

    def test_initialization(self):
        """Test tracker initializes with zero values."""
        tracker = WorkSessionTracker()
        assert tracker.sessions_completed == 0
        assert tracker.total_minutes == 0
        assert tracker.date == date.today()

    def test_add_completed_session_one(self):
        """Test adding one completed session."""
        tracker = WorkSessionTracker()
        tracker.add_completed_session(25)
        assert tracker.sessions_completed == 1
        assert tracker.total_minutes == 25

    def test_add_completed_session_multiple(self):
        """Test adding multiple completed sessions."""
        tracker = WorkSessionTracker()
        tracker.add_completed_session(25)
        tracker.add_completed_session(25)
        tracker.add_completed_session(25)
        assert tracker.sessions_completed == 3
        assert tracker.total_minutes == 75

    def test_get_stats_dict(self):
        """Test get_stats_dict() returns correct format."""
        tracker = WorkSessionTracker()
        tracker.add_completed_session(25)
        tracker.add_completed_session(25)
        
        stats = tracker.get_stats_dict()
        assert stats['completed'] == 2
        assert stats['totalMinutes'] == 50
        assert stats['date'] == date.today().isoformat()

    def test_is_same_day_today(self):
        """Test is_same_day() with today."""
        tracker = WorkSessionTracker()
        assert tracker.is_same_day() is True

    def test_is_same_day_future(self):
        """Test is_same_day() with future date."""
        tracker = WorkSessionTracker()
        future_date = date.today() + timedelta(days=1)
        assert tracker.is_same_day(future_date) is False

    def test_is_same_day_past(self):
        """Test is_same_day() with past date."""
        tracker = WorkSessionTracker()
        past_date = date.today() - timedelta(days=1)
        assert tracker.is_same_day(past_date) is False

    def test_reset_if_new_day_same_day(self):
        """Test reset_if_new_day() returns False on same day."""
        tracker = WorkSessionTracker()
        tracker.add_completed_session(25)
        reset_occurred = tracker.reset_if_new_day()
        
        assert reset_occurred is False
        assert tracker.sessions_completed == 1  # Not reset

    def test_reset_if_new_day_different_day(self):
        """Test reset_if_new_day() resets on different day."""
        tracker = WorkSessionTracker()
        tracker.add_completed_session(25)
        tracker.date = date.today() - timedelta(days=1)
        
        reset_occurred = tracker.reset_if_new_day()
        
        assert reset_occurred is True
        assert tracker.sessions_completed == 0
        assert tracker.total_minutes == 0
        assert tracker.date == date.today()

    def test_get_hours_minutes_str_zero_minutes(self):
        """Test get_hours_minutes_str() with zero minutes."""
        tracker = WorkSessionTracker()
        assert tracker.get_hours_minutes_str() == "0分"

    def test_get_hours_minutes_str_minutes_only(self):
        """Test get_hours_minutes_str() with minutes < 60."""
        tracker = WorkSessionTracker()
        tracker.total_minutes = 45
        assert tracker.get_hours_minutes_str() == "45分"

    def test_get_hours_minutes_str_hours_and_minutes(self):
        """Test get_hours_minutes_str() with hours and minutes."""
        tracker = WorkSessionTracker()
        tracker.total_minutes = 100  # 1時間40分
        assert tracker.get_hours_minutes_str() == "1時間40分"

    def test_get_hours_minutes_str_exact_hours(self):
        """Test get_hours_minutes_str() with exact hours."""
        tracker = WorkSessionTracker()
        tracker.total_minutes = 120  # 2時間0分
        assert tracker.get_hours_minutes_str() == "2時間0分"

    def test_workflow_multiple_sessions(self):
        """Test realistic workflow with multiple sessions."""
        tracker = WorkSessionTracker()
        
        # Session 1
        tracker.add_completed_session(25)
        assert tracker.sessions_completed == 1
        
        # Session 2
        tracker.add_completed_session(25)
        assert tracker.sessions_completed == 2
        assert tracker.total_minutes == 50
        
        # Session 3
        tracker.add_completed_session(25)
        assert tracker.sessions_completed == 3
        assert tracker.total_minutes == 75
        
        # Check stats
        stats = tracker.get_stats_dict()
        assert stats['completed'] == 3
        assert stats['totalMinutes'] == 75
        assert tracker.get_hours_minutes_str() == "1時間15分"
