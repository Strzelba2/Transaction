from exceptions import *
from validation import DataValidator
from data_factory import *

import logging
import os

class FileOperations:
    """
    Provides methods to read and write data to/from a file with a fixed-width format,
    ensuring all records are properly validated and structured. Handles operations
    such as reading, writing, validating the file structure, and maintaining currency consistency.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    def __init__(self, filename):
        """
        Initializes the FileOperations class with a specific file.

        Args:
            filename (str): The path to the file to be read or written.
        """
        self.filename = filename
        self.header = None
        self.transactions = []
        self.footer = None
        self.is_loaded = False
        self.currency = ""
        logging.debug(f"FileOperations initialized for file: {self.filename}")

    def read_file(self):
        """
        Reads and validates the file. Checks if the file exists and then validates its structure.
        Sets the global currency based on the first transaction to ensure consistency.
        Raises:
            FileFormatError: If the file does not exist, cannot be opened, or if the
                             file structure does not meet the required specifications.
        """
        if self.is_loaded:
            self.header = None
            self.transactions = []
            self.footer = None
            self.is_loaded = False
            self.currency = ""
            
        try:
            file_path = os.path.join( FileOperations.current_directory, 'files', self.filename)
            
            logging.debug(f"Checking if file exists: {file_path}")
            DataValidator.validate_file_exists(file_path)

            logging.debug(f"Opening file: {file_path}")
            with open(file_path, 'r') as file:
                lines = file.readlines()
                
            self.validate_and_set_currency(lines)

            logging.debug("Validating file structure.")
            DataValidator.validate_file_structure(lines)

            logging.info("File read and validated successfully.")
            
            header_data = DataFactory.parse_header_data(lines[0])
            self.header = DataFactory.create_header(header_data)
            
            for line in lines[1:-1]:
                transaction_data = DataFactory.parse_transaction_data(line)
                if transaction_data['currency'] != self.currency:
                    raise DataValidationError(f"Currency mismatch found: {transaction_data['currency']} does not match {self.currency}")
                transaction = DataFactory.create_transaction(transaction_data)
                self.transactions.append(transaction)
                
            footer_data = DataFactory.parse_footer_data(lines[-1])
            self.footer = DataFactory.create_footer(footer_data)
            
            self.is_loaded = True
            logging.info(f"File {self.filename} loaded and parsed successfully.")


        except FileNotFoundError as e:
            error_msg = f"File not found error: {str(e)}"
            logging.error(error_msg)
            raise 
        except DataValidationError as e:
            error_msg = f"Error validating file: {str(e)}"
            logging.error(error_msg)
            raise FileFormatError(error_msg)
        except DataFactorError as e:
            error_msg = f"Data creation error: {str(e)}"
            logging.error(error_msg)
            raise 
        except Exception as e:
            error_msg = f"Error reading or validating file: {str(e)}"
            logging.error(error_msg)
            raise FileFormatError(error_msg)

    def get_field_value(self, record_type, field_name, counter_value=None):
        """
        Retrieves the value of a specified field from a loaded file's record,
        either header, transaction, or footer based on record_type.
        Args:
            record_type (str): The type of record ('header', 'transaction', 'footer').
            field_name (str): The name of the field to retrieve.
            counter_value (str): The counter value of the transaction, if applicable.
        Returns:
            The value of the field, or an error message if the field cannot be found.
        """
        if not self.is_loaded:
            logging.error("Attempted to access fields before the file was loaded.")
            return "No file loaded or file load failed."
        
        logging.debug(f"Retrieving field value: record_type={record_type}, field_name={field_name}, counter_value={counter_value}")
        try:
            if record_type == "header" and self.header:
                return getattr(self.header, field_name, None)
            elif record_type == "footer" and self.footer:
                return getattr(self.footer, field_name, None)
            elif record_type == "transaction" and self.transactions:
                formatted_counter_value = f"{counter_value:0>6}"
                transaction = next((t for t in self.transactions if getattr(t, 'counter', '') == formatted_counter_value), None)
                if transaction:
                    return getattr(transaction, field_name, None)
                else:
                    return f"No transaction found with counter {formatted_counter_value}."
            else:
                return "Invalid record type specified."
        except Exception as e:
            logging.error(f"Error retrieving field value: {e}")
            return f"Error: {e}"
    
    def save_file(self):
        """
        Writes the current data (header, transactions, footer) back to the file, ensuring all data conforms to the fixed-width format.
        Raises:
            FileFormatError: If there is an error during file writing.
        """
        try:
            file_path = os.path.join( FileOperations.current_directory, 'files', self.filename)
            
            logging.debug(f"Saving file to: {file_path}")
            DataValidator.validate_file_exists(file_path)
            
            with open(file_path, 'w') as file:
                file.write(self.header.to_fixed_width_string() + '\n')
                for transaction in self.transactions:
                    file.write(transaction.to_fixed_width_string() + '\n')
                file.write(self.footer.to_fixed_width_string() + '\n')
            logging.info(f"File {self.filename} saved successfully.")
                
        except FileNotFoundError as e:
            error_msg = f"File not found error during save: {e}"
            logging.error(error_msg)
            raise 
        except Exception as e:
            logging.error(f"Error reading or validating file: {str(e)}")
            error_msg = f"Error reading or validating file: {str(e)}"
            raise FileFormatError(error_msg)
        
    def validate_and_set_currency(self, lines):
        """
        Validates the currency in the first transaction and sets it for the entire file.
        Raises:
            DataValidationError: If the currency is not allowed or inconsistent.
        """
        logging.debug(f"validate_and_set_currency")
        first_transaction_data = DataFactory.parse_transaction_data(lines[1])
        currency = first_transaction_data['currency']
        if currency not in DataValidator.ALLOWED_CURRENCIES:
            error_msg = f"Invalid currency in the first transaction: {currency}"
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        self.currency = currency
        logging.debug(f"Currency set to {self.currency} for all transactions.")
        
    def update_footer(self, amount):
        """
        Updates the total_counter and control_sum in the footer based on new transactions.
        """
        new_total_counter = f"{int(self.footer.total_counter) + 1:06d}"
        new_control_sum = f"{float(self.footer.control_sum) + float(amount):.2f}".rjust(12, '0')
        
        logging.debug(f"Updating footer: new total_counter={new_total_counter}, new control_sum={new_control_sum}")
        try:
            DataValidator.validate_field(self.footer, "control_sum", new_control_sum)
            DataValidator.validate_field(self.footer, "total_counter", new_total_counter)
        except DataValidationError as e:
            logging.error(f"Error updating footer: {e}")
            raise