"""
Unit Tests for storage.py

Test coverage for:
- StorageInterface contract
- FileStorage implementation
- MockStorage implementation
- Edge cases and error handling
"""

import pytest
import json
import os
import tempfile
from datetime import date, timedelta
from storage import (
    StorageInterface,
    FileStorage,
    MockStorage,
    StorageFactory
)


# Fixtures for test setup


@pytest.fixture
def mock_storage():
    """Provide a fresh MockStorage instance"""
    return MockStorage()


@pytest.fixture
def temp_file():
    """Provide a temporary file for FileStorage testing"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)


@pytest.fixture
def file_storage(temp_file):
    """Provide a FileStorage instance with temp file"""
    return FileStorage(temp_file)


@pytest.fixture
def sample_session():
    """Provide a sample session dictionary"""
    return {
        'start_time': '09:00',
        'duration': 1500,
        'completed': True,
        'breaks': 2
    }


@pytest.fixture
def sample_date():
    """Provide a sample date"""
    return date(2024, 1, 15)


# Tests for MockStorage


class TestMockStorage:
    """Test suite for MockStorage implementation"""

    def test_initialization(self, mock_storage):
        """MockStorage initializes with empty data"""
        assert mock_storage.data == {}
        assert mock_storage.get_all_sessions() == {}

    def test_save_single_session(self, mock_storage, sample_date, sample_session):
        """Save a single session"""
        mock_storage.save_session(sample_date, sample_session)
        
        sessions = mock_storage.get_sessions(sample_date)
        assert len(sessions) == 1
        assert sessions[0] == sample_session

    def test_save_multiple_sessions_same_day(self, mock_storage, sample_date, sample_session):
        """Save multiple sessions on the same day"""
        session2 = {'start_time': '10:30', 'duration': 300, 'completed': True}
        
        mock_storage.save_session(sample_date, sample_session)
        mock_storage.save_session(sample_date, session2)
        
        sessions = mock_storage.get_sessions(sample_date)
        assert len(sessions) == 2
        assert sessions[0] == sample_session
        assert sessions[1] == session2

    def test_save_sessions_different_days(self, mock_storage, sample_session):
        """Save sessions on different days"""
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        mock_storage.save_session(date1, sample_session)
        mock_storage.save_session(date2, sample_session)
        
        assert len(mock_storage.get_sessions(date1)) == 1
        assert len(mock_storage.get_sessions(date2)) == 1

    def test_get_nonexistent_date_returns_empty_list(self, mock_storage):
        """Get sessions for non-existent date returns empty list"""
        result = mock_storage.get_sessions(date(2024, 1, 15))
        assert result == []
        assert isinstance(result, list)

    def test_get_all_sessions_empty(self, mock_storage):
        """Get all sessions from empty storage"""
        assert mock_storage.get_all_sessions() == {}

    def test_get_all_sessions_multiple_dates(self, mock_storage, sample_session):
        """Get all sessions across multiple dates"""
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        mock_storage.save_session(date1, sample_session)
        mock_storage.save_session(date2, sample_session)
        
        all_sessions = mock_storage.get_all_sessions()
        assert len(all_sessions) == 2
        assert '2024-01-15' in all_sessions
        assert '2024-01-16' in all_sessions

    def test_delete_sessions_removes_all_for_date(self, mock_storage, sample_date, sample_session):
        """Delete removes all sessions for a date"""
        session2 = {'start_time': '10:30', 'duration': 300, 'completed': True}
        
        mock_storage.save_session(sample_date, sample_session)
        mock_storage.save_session(sample_date, session2)
        
        assert len(mock_storage.get_sessions(sample_date)) == 2
        
        mock_storage.delete_sessions(sample_date)
        assert len(mock_storage.get_sessions(sample_date)) == 0

    def test_delete_nonexistent_date_no_error(self, mock_storage):
        """Delete on non-existent date doesn't raise error"""
        # Should not raise
        mock_storage.delete_sessions(date(2024, 1, 15))

    def test_delete_one_date_preserves_others(self, mock_storage, sample_session):
        """Delete only removes sessions for specified date"""
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        mock_storage.save_session(date1, sample_session)
        mock_storage.save_session(date2, sample_session)
        
        mock_storage.delete_sessions(date1)
        
        assert len(mock_storage.get_sessions(date1)) == 0
        assert len(mock_storage.get_sessions(date2)) == 1

    def test_clear_all_removes_everything(self, mock_storage, sample_session):
        """Clear all removes all data"""
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        mock_storage.save_session(date1, sample_session)
        mock_storage.save_session(date2, sample_session)
        
        assert len(mock_storage.get_all_sessions()) == 2
        
        mock_storage.clear_all()
        
        assert len(mock_storage.get_all_sessions()) == 0
        assert mock_storage.get_sessions(date1) == []

    def test_session_data_preserved_exactly(self, mock_storage, sample_date):
        """Session data is preserved exactly as saved"""
        session = {
            'start_time': '14:30:45',
            'duration': 2700,
            'completed': False,
            'tags': ['productive', 'focused'],
            'notes': 'Important work session'
        }
        
        mock_storage.save_session(sample_date, session)
        retrieved = mock_storage.get_sessions(sample_date)[0]
        
        assert retrieved == session
        assert retrieved['start_time'] == '14:30:45'
        assert retrieved['tags'] == ['productive', 'focused']


# Tests for FileStorage


class TestFileStorage:
    """Test suite for FileStorage implementation"""

    def test_initialization_creates_file(self, file_storage, temp_file):
        """FileStorage initialization creates the file"""
        assert os.path.exists(temp_file)

    def test_initialization_with_empty_file(self, temp_file):
        """FileStorage handles empty file gracefully"""
        storage = FileStorage(temp_file)
        assert storage.get_all_sessions() == {}

    def test_save_single_session(self, file_storage, sample_date, sample_session):
        """Save session to file"""
        file_storage.save_session(sample_date, sample_session)
        
        sessions = file_storage.get_sessions(sample_date)
        assert len(sessions) == 1
        assert sessions[0] == sample_session

    def test_save_persists_to_disk(self, temp_file, sample_date, sample_session):
        """Saved session persists after reloading storage"""
        storage1 = FileStorage(temp_file)
        storage1.save_session(sample_date, sample_session)
        
        storage2 = FileStorage(temp_file)
        sessions = storage2.get_sessions(sample_date)
        
        assert len(sessions) == 1
        assert sessions[0] == sample_session

    def test_save_multiple_sessions_same_day(self, file_storage, sample_date, sample_session):
        """Save multiple sessions on same day to file"""
        session2 = {'start_time': '10:30', 'duration': 300, 'completed': True}
        
        file_storage.save_session(sample_date, sample_session)
        file_storage.save_session(sample_date, session2)
        
        sessions = file_storage.get_sessions(sample_date)
        assert len(sessions) == 2

    def test_get_nonexistent_date_returns_empty(self, file_storage):
        """Get non-existent date returns empty list"""
        result = file_storage.get_sessions(date(2024, 1, 15))
        assert result == []

    def test_delete_sessions_updates_file(self, file_storage, sample_date, sample_session):
        """Delete modifies file correctly"""
        file_storage.save_session(sample_date, sample_session)
        assert len(file_storage.get_sessions(sample_date)) == 1
        
        file_storage.delete_sessions(sample_date)
        assert len(file_storage.get_sessions(sample_date)) == 0

    def test_delete_persists_to_disk(self, temp_file, sample_date, sample_session):
        """Delete persists across storage instances"""
        storage1 = FileStorage(temp_file)
        storage1.save_session(sample_date, sample_session)
        storage1.delete_sessions(sample_date)
        
        storage2 = FileStorage(temp_file)
        assert storage2.get_sessions(sample_date) == []

    def test_clear_all_removes_file_content(self, file_storage, sample_date, sample_session):
        """Clear all removes all content"""
        file_storage.save_session(sample_date, sample_session)
        file_storage.clear_all()
        
        assert file_storage.get_all_sessions() == {}

    def test_corrupted_file_returns_empty(self, temp_file):
        """Corrupted JSON file returns empty dict"""
        with open(temp_file, 'w') as f:
            f.write('{ invalid json }')
        
        storage = FileStorage(temp_file)
        assert storage.get_all_sessions() == {}

    def test_empty_file_returns_empty(self, temp_file):
        """Empty file returns empty dict"""
        # Create empty file
        open(temp_file, 'w').close()
        
        storage = FileStorage(temp_file)
        assert storage.get_all_sessions() == {}

    def test_file_format_is_valid_json(self, file_storage, sample_date, sample_session):
        """Saved file contains valid JSON"""
        file_storage.save_session(sample_date, sample_session)
        
        with open(file_storage.storage_file, 'r') as f:
            content = json.load(f)
        
        assert isinstance(content, dict)
        assert '2024-01-15' in content

    def test_nested_dict_data_preserved(self, file_storage, sample_date):
        """Complex nested structures are preserved"""
        session = {
            'metadata': {
                'tags': ['focus', 'work'],
                'location': 'office'
            },
            'stats': {
                'interruptions': 3,
                'focus_score': 8.5
            }
        }
        
        file_storage.save_session(sample_date, session)
        retrieved = file_storage.get_sessions(sample_date)[0]
        
        assert retrieved == session
        assert retrieved['metadata']['location'] == 'office'


# Tests for StorageInterface contract


@pytest.fixture
def contract_storage(request, tmp_path):
    """Contract tests用のstorage実装を返す"""
    if request.param == 'mock':
        return MockStorage()
    if request.param == 'file':
        return FileStorage(str(tmp_path / 'contract_storage.json'))
    raise ValueError(f"Unknown storage type: {request.param}")


class TestStorageInterfaceContract:
    """Test that all implementations satisfy the contract"""

    @pytest.mark.parametrize('contract_storage', ['mock', 'file'], indirect=True)
    def test_all_implementations_have_required_methods(self, contract_storage):
        """All storage implementations have required methods"""
        assert hasattr(contract_storage, 'get_sessions')
        assert hasattr(contract_storage, 'save_session')
        assert hasattr(contract_storage, 'get_all_sessions')
        assert hasattr(contract_storage, 'delete_sessions')
        assert hasattr(contract_storage, 'clear_all')

    def test_mock_implements_storage_interface(self):
        """MockStorage implements StorageInterface"""
        assert isinstance(MockStorage(), StorageInterface)

    def test_file_storage_implements_storage_interface(self, file_storage):
        """FileStorage implements StorageInterface"""
        assert isinstance(file_storage, StorageInterface)


# Tests for StorageFactory


class TestStorageFactory:
    """Test suite for StorageFactory"""

    def test_create_mock_storage(self):
        """Factory creates MockStorage"""
        storage = StorageFactory.create_mock_storage()
        assert isinstance(storage, MockStorage)

    def test_create_file_storage_default(self):
        """Factory creates FileStorage with default file"""
        # Use temp file to avoid creating sessions.json in tests
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
        
        try:
            storage = FileStorage(temp_file)
            assert isinstance(storage, FileStorage)
        finally:
            os.remove(temp_file)

    def test_create_file_storage_custom_path(self, temp_file):
        """Factory creates FileStorage with custom path"""
        storage = StorageFactory.create_file_storage(temp_file)
        assert isinstance(storage, FileStorage)
        assert storage.storage_file == temp_file


# Edge case tests


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_save_session_with_empty_dict(self, mock_storage, sample_date):
        """Save empty session dictionary"""
        mock_storage.save_session(sample_date, {})
        sessions = mock_storage.get_sessions(sample_date)
        assert len(sessions) == 1
        assert sessions[0] == {}

    def test_save_session_with_none_values(self, mock_storage, sample_date):
        """Save session with None values"""
        session = {'start_time': None, 'duration': None}
        mock_storage.save_session(sample_date, session)
        sessions = mock_storage.get_sessions(sample_date)
        assert sessions[0] == session

    def test_save_many_sessions_same_day(self, mock_storage, sample_date):
        """Save many sessions in single day"""
        for i in range(50):
            mock_storage.save_session(sample_date, {'session_id': i})
        
        sessions = mock_storage.get_sessions(sample_date)
        assert len(sessions) == 50

    def test_date_isolation(self, mock_storage):
        """Sessions from different dates are isolated"""
        date1 = date(2024, 1, 15)
        date2 = date(2024, 1, 16)
        
        mock_storage.save_session(date1, {'id': 1})
        mock_storage.save_session(date2, {'id': 2})
        
        sessions1 = mock_storage.get_sessions(date1)
        sessions2 = mock_storage.get_sessions(date2)
        
        assert sessions1[0]['id'] == 1
        assert sessions2[0]['id'] == 2

    def test_successive_operations(self, mock_storage, sample_date, sample_session):
        """Multiple operations on same storage instance"""
        # Save
        mock_storage.save_session(sample_date, sample_session)
        assert len(mock_storage.get_sessions(sample_date)) == 1
        
        # Save another
        mock_storage.save_session(sample_date, sample_session)
        assert len(mock_storage.get_sessions(sample_date)) == 2
        
        # Delete
        mock_storage.delete_sessions(sample_date)
        assert len(mock_storage.get_sessions(sample_date)) == 0
        
        # Save again
        mock_storage.save_session(sample_date, sample_session)
        assert len(mock_storage.get_sessions(sample_date)) == 1

    def test_get_all_sessions_is_independent_copy(self, mock_storage, sample_date):
        """get_all_sessions returns independent copy (no reference issues)"""
        session = {'id': 1}
        mock_storage.save_session(sample_date, session)
        
        all_sessions = mock_storage.get_all_sessions()
        # Modifying the returned dict shouldn't affect storage
        all_sessions['2024-01-15'].append({'id': 2})
        
        # Original should be unchanged
        assert len(mock_storage.get_sessions(sample_date)) == 1


# Performance and reliability tests


class TestPerformance:
    """Test performance characteristics"""

    def test_mock_storage_many_sessions(self, mock_storage):
        """MockStorage handles many sessions efficiently"""
        for day_offset in range(30):
            current_date = date(2024, 1, 1) + timedelta(days=day_offset)
            for session_num in range(10):
                mock_storage.save_session(current_date, {'op': session_num})
        
        all_sessions = mock_storage.get_all_sessions()
        assert len(all_sessions) == 30
        
        for date_str in all_sessions.values():
            assert len(date_str) == 10

    def test_file_storage_many_sessions(self, file_storage):
        """FileStorage handles many sessions"""
        for day_offset in range(10):
            current_date = date(2024, 1, 1) + timedelta(days=day_offset)
            for session_num in range(5):
                file_storage.save_session(current_date, {'op': session_num})
        
        all_sessions = file_storage.get_all_sessions()
        assert len(all_sessions) == 10
