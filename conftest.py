import pytest
from cli import CLI
from file_operations import FileOperations
from configuration import Config
from exceptions import *
from unittest.mock import mock_open, MagicMock, Mock

@pytest.fixture
def cli():
    """Fixture to create a CLI instance with mocked FileOperations."""
    cli_instance = CLI()
    cli_instance.file_ops = MagicMock(spec=FileOperations)
    cli_instance.config = MagicMock(spec=Config)
    return cli_instance

@pytest.fixture
def setup_file_operations(mocker):
    """Fixture to mock file_operations used in CLI."""
    mocker.patch('file_operations.FileOperations.read_file')
    mocker.patch('file_operations.FileOperations.save_file')
    return FileOperations