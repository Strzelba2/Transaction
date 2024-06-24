import pytest
from conftest import *
from exceptions import *
from models import * 
import logging



def test_load_file_success(cli, setup_file_operations, mocker):
    """Test if loading a file successfully sets up file operations correctly.
    
    Args:
        cli (CLI): Instance of the CLI class.
        setup_file_operations (Mock): Mocked FileOperations setup.
        mocker (MockerFixture): Pytest mocker fixture.
    
    This test ensures that the 'read_file' method is called once and that file operations are initialized properly after loading a file.
    """
    mocker.patch('builtins.open', mocker.mock_open(read_data="data"))
    cli.do_load('testfile.txt')
    setup_file_operations.read_file.assert_called_once()
    assert cli.file_ops is not None
    
def test_load_file_not_found(cli, mocker, capfd):
    """
    Test handling of an attempt to load a non-existent file.

    Verifies that the system correctly handles and reports an error when trying to load a file that does not exist.
    """
    mocker.patch('file_operations.FileOperations.read_file', side_effect=FileNotFoundError)
    cli.do_load('nonexistent.txt')
    captured = capfd.readouterr()  
    assert "File not found" in captured.out
    assert "Please check the file path and try loading again." in captured.out
    
def test_handle_permission_error_on_load(cli, mocker, capfd):
    """
    Test handling of a permission error during file loading.

    Verifies that the CLI correctly handles permission errors when attempting to open a file, by checking the error messaging.
    """
    mocker.patch('file_operations.FileOperations.read_file', side_effect=PermissionError)
    cli.do_load('nonexistent.txt')
    captured = capfd.readouterr()  
    assert "Check your file permissions." in captured.out
    
def test_load_file_with_valid_currency(cli, mocker, capfd):
    """
    Test loading a file with a valid currency designation.

    Ensures that a file containing valid currency codes does not cause any load errors and that the load is reported as successful.
    """
    valid_currency_data = "01...USD...\n02...100.00...USD...\n03..."
    mocker.patch('builtins.open', mocker.mock_open(read_data=valid_currency_data))
    mocker.patch('file_operations.FileOperations.read_file')
    
    cli.do_load('valid_currency.txt')
    output, _ = capfd.readouterr()
    assert "loaded successfully" in output
    
def test_load_file_with_invalid_currency(cli, mocker, capfd, caplog):
    """
    Test loading a file with an invalid currency code.

    Ensures the CLI identifies and reports files with unsupported currency codes during the file validation phase.
    """
    caplog.set_level(logging.DEBUG)
    # Mock read_file to simulate reading a file with an invalid currency
    invalid_currency_data = "01...XYZ...\n02...100.00...XYZ...\n03..."
    mocker.patch('builtins.open', mocker.mock_open(read_data=invalid_currency_data), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')

    cli.do_load('invalid_currency.txt')
    output, _ = capfd.readouterr()
    assert "Invalid currency in the first transaction" in output
    
def test_load_file_with_too_long_lines(cli, mocker, capfd, caplog):
    """
    Test loading a file where one or more lines exceed the expected line length.

    Verifies that the system correctly identifies and reports lines that do not conform to the expected length.
    """
    caplog.set_level(logging.DEBUG)
    too_long_line_data = "01" + "A" * 119 + "\n"+"02" + "A" * 117 + "\n" +"03" + "A" * 110 + "\n" 
    mocker.patch('builtins.open', mocker.mock_open(read_data=too_long_line_data), create=True)

    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')

    cli.do_load('faulty_file.txt')
    output, _ = capfd.readouterr()

    assert "Each line must be exactly 120 characters long" in output
    
def test_load_file_with_one_line(cli, mocker, capfd, caplog):
    """
    Test loading a file that does not meet the minimum requirement for the number of lines.

    Ensures the CLI correctly identifies and reports files that lack the mandatory header, transaction, and footer records.
    """
    caplog.set_level(logging.DEBUG)
    one_line_data = "01" + "A" * 117 + "\n"  
    mocker.patch('builtins.open', mocker.mock_open(read_data=one_line_data))

    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    
    cli.do_load('faulty_file.txt')
    output, _ = capfd.readouterr()

    assert "File must contain at least one header, one transaction, and one footer" in output
    
def test_load_file_headers_lines(cli, mocker, capfd, caplog):
    """
    Test loading a file that improperly starts or ends with incorrect record types.

    Verifies that the CLI enforces the correct order of records in the file: a header at the start and a footer at the end.
    """
    caplog.set_level(logging.DEBUG)
    too_long_line_data = "03" + "A" * 118 + "\n"+"02" + "A" * 118 + "\n" +"03" + "A" * 118 + "\n" 
    mocker.patch('builtins.open', mocker.mock_open(read_data=too_long_line_data), create=True)

    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')

    cli.do_load('faulty_file.txt')
    output, _ = capfd.readouterr()

    assert "File must start with a header and end with a footer" in output
    
def test_load_file_header_transaction(cli, mocker, capfd, caplog):
    """
    Test loading a file with incorrect transaction record identifiers.

    Ensures that each transaction record starts with the correct identifier and that errors are reported when this is not the case.
    """
    caplog.set_level(logging.DEBUG)
    too_long_line_data = "01" + "A" * 118 + "\n"+"01" + "A" * 118 + "\n" +"03" + "A" * 118 + "\n" 
    mocker.patch('builtins.open', mocker.mock_open(read_data=too_long_line_data), create=True)

    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')

    cli.do_load('faulty_file.txt')
    output, _ = capfd.readouterr()

    assert "Each transaction must start with 02 id" in output
    
def test_do_load_with_valid_header_data(cli, mocker, capfd, caplog):
    """
    Test loading a file with correct header data.

    Validates that the header data is parsed and stored correctly when a valid header is loaded.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "01                       Artur                    Strzelczyk                            AS           1594 Some Street NY"
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_footer_data')
    mocker.patch('data_factory.DataFactory.create_footer')

    cli.do_load('dummy_filename.txt')
    output, _ = capfd.readouterr()
    assert "File 'dummy_filename.txt' loaded successfully." in output
    
def test_do_load_with_valid_footer_data(cli, mocker, capfd, caplog):
    """
    Test loading a file with correct footer data.

    Validates that the footer data is parsed and stored correctly when a valid footer is loaded.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "03000007000004798.54                                                                                                    "
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_header_data')
    mocker.patch('data_factory.DataFactory.create_header')

    cli.do_load('dummy_filename.txt')
    output, _ = capfd.readouterr()
    assert "File 'dummy_filename.txt' loaded successfully." in output
    
def test_do_load_with_invalid_footer_data(cli, mocker, capfd, caplog):
    """
    Test loading a file with incorrect footer data, specifically invalid numerical data.

    Ensures that errors are caught and reported when footer data contains invalid numerical formats.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "030000070000-4798.54                                                                                                    "
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_header_data')
    mocker.patch('data_factory.DataFactory.create_header')

    cli.do_load('dummy_filename.txt')
    output, _ = capfd.readouterr()
    assert "Expected a float, got <class 'str'>" in output
    
    
def test_get_field_footer(cli, mocker, capfd, caplog):
    """
    Test retrieval of a valid field from the footer.

    Confirms that correct data retrieval from the footer is functional and returns the expected values.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "03000007000004798.54                                                                                                    "
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_header_data')
    mocker.patch('data_factory.DataFactory.create_header')

    cli.do_load('dummy_filename.txt')
    cli.do_get_field('footer total_counter')
    output, _ = capfd.readouterr()
    assert "000007" in output
    
def test_get_invalid_field_footer(cli, mocker, capfd, caplog):
    """
    Test retrieval of a non-existent field from the footer.

    Verifies that the system properly handles requests for fields that do not exist within the footer, returning appropriate error messages.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "03000007000004798.54                                                                                                    "
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_header_data')
    mocker.patch('data_factory.DataFactory.create_header')

    cli.do_load('dummy_filename.txt')
    cli.do_get_field('footer name')
    output, _ = capfd.readouterr()
    assert "Field not found or invalid parameters" in output
    
def test_get_field_header(cli, mocker, capfd, caplog):
    """
    Test retrieval of a valid field from the header.

    Confirms that correct data retrieval from the header is functional and returns the expected values.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "01                       Artur                    Strzelczyk                            AS           1594 Some Street NY"
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_footer_data')
    mocker.patch('data_factory.DataFactory.create_footer')

    cli.do_load('dummy_filename.txt')
    cli.do_get_field('header name')
    output, _ = capfd.readouterr()
    assert "Artur" in output
    
def test_get_invalid_field_header(cli, mocker, capfd, caplog):
    """
    Test retrieval of a non-existent field from the header.

    Ensures that the CLI correctly reports errors when attempting to access a header field that does not exist.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "01                       Artur                    Strzelczyk                            AS           1594 Some Street NY"
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_footer_data')
    mocker.patch('data_factory.DataFactory.create_footer')

    cli.do_load('dummy_filename.txt')
    cli.do_get_field('header czeslaw')
    output, _ = capfd.readouterr()
    assert "Field not found or invalid parameters" in output
    
def test_lock_and_unlock_field(cli, mocker):
    """
    Test locking and unlocking a field to ensure field editability is managed correctly.

    This test verifies the functionality of dynamically changing the editability state of fields via configuration.
    """
    mocker.patch('configuration.Config.save_lock_config')
    mocker.patch('configuration.Config.load_lock_config')
    cli.config.lock_config = {'header': {'name': False}}
    cli.do_lock('header name')
    assert cli.config.lock_config['header']['name'] == True

    cli.do_unlock('header name')
    assert cli.config.lock_config['header']['name'] == False
    
def test_set_field_header(cli, mocker, capfd, caplog):
    """
    Test setting a field value in the header when it is not locked.

    Ensures that changes to header fields are correctly applied and persisted when the field is not locked.
    """
    caplog.set_level(logging.DEBUG)
    header_line = "01                       Artur                    Strzelczyk                            AS           1594 Some Street NY"
    mocker.patch('builtins.open', mocker.mock_open(read_data=header_line), create=True)
    mocker.patch('validation.DataValidator.validate_file_exists')
    mocker.patch('file_operations.FileOperations.validate_and_set_currency')
    mocker.patch('validation.DataValidator.validate_file_structure')
    
    mocker.patch('data_factory.DataFactory.parse_footer_data')
    mocker.patch('data_factory.DataFactory.create_footer')
    
    mocker.patch('configuration.Config.save_lock_config')
    mocker.patch('configuration.Config.load_lock_config')
    cli.config.lock_config = {'header': {'name': False}}

    cli.do_load('dummy_filename.txt')
    cli.do_set_field("header name JohnDoe")
    cli.do_get_field('header name')
    output, _ = capfd.readouterr()
    assert "JohnDoe" in output
    
def test_add_transaction_valid(cli, mocker):
    """
    Test the addition of a valid transaction and its effect on the system state.

    Checks whether adding a transaction correctly updates the transaction list and footer totals.
    """
    cli.file_ops.currency = 'USD'
    cli.file_ops.transactions = []
    mocker.patch('data_factory.DataFactory.create_transaction')
    cli.do_add_transaction('100')
    assert len(cli.file_ops.transactions) == 1
    cli.file_ops.save_file.assert_called()
    


