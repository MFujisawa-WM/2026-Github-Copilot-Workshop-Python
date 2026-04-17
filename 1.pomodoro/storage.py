"""
Storage Layer - Session persistence and retrieval

This module provides an abstraction for session data storage,
allowing for different storage backends (file-based, database, etc.)
without changing the business logic.

Architecture:
- StorageInterface: Abstract base class defining the storage contract
- FileStorage: Concrete implementation using JSON files
- MockStorage: Test implementation for dependency injection
"""

from abc import ABC, abstractmethod
import json
import os
import copy
from datetime import datetime, date
from typing import Dict, List, Optional, Any


class StorageInterface(ABC):
    """Abstract base class for storage backends"""

    @abstractmethod
    def get_sessions(self, session_date: date) -> List[Dict[str, Any]]:
        """
        Get all sessions for a specific date
        
        Args:
            session_date: Date to retrieve sessions for
            
        Returns:
            List of session dictionaries with keys: start_time, duration, completed
        """
        pass

    @abstractmethod
    def save_session(self, session_date: date, session: Dict[str, Any]) -> None:
        """
        Save a completed session
        
        Args:
            session_date: Date of the session
            session: Session data (start_time, duration, completed, etc.)
        """
        pass

    @abstractmethod
    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all sessions ever recorded
        
        Returns:
            Dictionary with date strings as keys and session lists as values
        """
        pass

    @abstractmethod
    def delete_sessions(self, session_date: date) -> None:
        """
        Delete all sessions for a specific date
        
        Args:
            session_date: Date to delete sessions for
        """
        pass

    @abstractmethod
    def clear_all(self) -> None:
        """Remove all stored data"""
        pass


class FileStorage(StorageInterface):
    """
    File-based storage using JSON format
    
    Storage structure:
    {
        "2024-01-15": [
            {"start_time": "09:00", "duration": 1500, "completed": true},
            {"start_time": "09:30", "duration": 1500, "completed": false},
            ...
        ],
        "2024-01-16": [...]
    }
    """

    def __init__(self, storage_file: str = 'sessions.json'):
        """
        Initialize file-based storage
        
        Args:
            storage_file: Path to JSON file for storing sessions
        """
        self.storage_file = storage_file
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create storage file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump({}, f)

    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load data from storage file"""
        try:
            with open(self.storage_file, 'r') as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except (json.JSONDecodeError, IOError):
            # Return empty dict if file is corrupted or unreadable
            return {}

    def _save_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save data to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to write to storage file: {e}")

    def get_sessions(self, session_date: date) -> List[Dict[str, Any]]:
        """Get all sessions for a specific date"""
        data = self._load_data()
        date_key = session_date.isoformat()
        return data.get(date_key, [])

    def save_session(self, session_date: date, session: Dict[str, Any]) -> None:
        """Save a completed session"""
        data = self._load_data()
        date_key = session_date.isoformat()
        
        if date_key not in data:
            data[date_key] = []
        
        data[date_key].append(session)
        self._save_data(data)

    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all sessions ever recorded"""
        return self._load_data()

    def delete_sessions(self, session_date: date) -> None:
        """Delete all sessions for a specific date"""
        data = self._load_data()
        date_key = session_date.isoformat()
        
        if date_key in data:
            del data[date_key]
            self._save_data(data)

    def clear_all(self) -> None:
        """Remove all stored data"""
        self._save_data({})


class MockStorage(StorageInterface):
    """
    In-memory mock storage for testing
    
    Implements StorageInterface without file I/O for fast unit tests
    """

    def __init__(self):
        """Initialize mock storage with empty data"""
        self.data: Dict[str, List[Dict[str, Any]]] = {}

    def get_sessions(self, session_date: date) -> List[Dict[str, Any]]:
        """Get all sessions for a specific date"""
        date_key = session_date.isoformat()
        return self.data.get(date_key, [])

    def save_session(self, session_date: date, session: Dict[str, Any]) -> None:
        """Save a completed session"""
        date_key = session_date.isoformat()
        
        if date_key not in self.data:
            self.data[date_key] = []
        
        self.data[date_key].append(session)

    def get_all_sessions(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all sessions ever recorded"""
        return copy.deepcopy(self.data)

    def delete_sessions(self, session_date: date) -> None:
        """Delete all sessions for a specific date"""
        date_key = session_date.isoformat()
        
        if date_key in self.data:
            del self.data[date_key]

    def clear_all(self) -> None:
        """Remove all stored data"""
        self.data.clear()


class StorageFactory:
    """Factory for creating storage instances"""

    @staticmethod
    def create_file_storage(filename: str = 'sessions.json') -> FileStorage:
        """Create file-based storage instance"""
        return FileStorage(filename)

    @staticmethod
    def create_mock_storage() -> MockStorage:
        """Create mock storage instance for testing"""
        return MockStorage()
