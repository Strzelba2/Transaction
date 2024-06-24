from models import Header, Transaction, Footer
from exceptions import DataValidationError , DataFactorError
import logging

class DataFactory:
    """
    A factory class responsible for creating and parsing data entities
    such as headers, transactions, and footers from fixed-width formatted strings.
    It handles data validation and construction, ensuring that each entity conforms
    to the expected format before instantiation.
    """
    @staticmethod
    def create_header(data):
        """
        Creates a Header instance from a dictionary of data, ensuring validation.
        Logs the creation process and errors.
        
        Args:
            data (dict): Data needed to instantiate a Header.
        
        Returns:
            Header: An instance of Header initialized with the provided data.
        
        Raises:
            DataFactorError: If there is a validation error during header creation.
        """
        logging.debug("Attempting to create header with data: %s", data)
        try:
            header = Header(**data)
            logging.info("Header created successfully: %s", header)
            return header
        except DataValidationError as e:
            error_msg = f"Error creating header: {e}"
            logging.error(error_msg)
            raise DataFactorError(error_msg)

    @staticmethod
    def create_transaction(data):
        """
        Creates a Transaction instance from a dictionary of data, ensuring validation.
        Logs the creation process and errors.
        
        Args:
            data (dict): Data needed to instantiate a Transaction.
        
        Returns:
            Transaction: An instance of Transaction initialized with the provided data.
        
        Raises:
            DataFactorError: If there is a validation error during transaction creation.
        """
        logging.debug("Attempting to create transaction with data: %s", data)
        try:
            transaction = Transaction(**data)
            logging.info("Transaction created successfully: %s", transaction)
            return transaction
        except DataValidationError as e:
            error_msg = f"Error creating transaction: {e}"
            logging.error(error_msg)
            raise DataFactorError(error_msg)

    @staticmethod
    def create_footer(data):
        """
        Creates a Footer instance from a dictionary of data, ensuring validation.
        Logs the creation process and errors.
        
        Args:
            data (dict): Data needed to instantiate a Footer.
        
        Returns:
            Footer: An instance of Footer initialized with the provided data.
        
        Raises:
            DataFactorError: If there is a validation error during footer creation.
        """
        logging.debug("Attempting to create footer with data: %s", data)
        try:
            footer = Footer(**data)
            logging.info("Footer created successfully: %s", footer)
            return footer
        except DataValidationError as e:
            error_msg = f"Error creating footer: {e}"
            logging.error(error_msg)
            raise DataFactorError(error_msg)

    @staticmethod
    def parse_header_data(data):
        """
        Parses raw string data to extract header fields according to the fixed format.
        
        Args:
            data (str): Raw data string for the header.
        
        Returns:
            dict: Parsed data dictionary for header creation.
        
        Raises:
            DataValidationError: If the field ID does not match the expected header ID.
        """

        if data[0:2].strip() != "01":
            raise DataValidationError("Field ID for header must be '01'.")
        
        field_data = {
            "name": data[2:30].strip(),
            "surname": data[30:60].strip(),
            "patronymic": data[60:90].strip(),
            "address": data[90:120].strip()
        }

        return field_data

    @staticmethod
    def parse_transaction_data(data):
        """
        Parses raw string data to extract transaction fields according to the fixed format.
        
        Args:
            data (str): Raw data string for the transaction.
        
        Returns:
            dict: Parsed data dictionary for transaction creation.
        
        Raises:
            DataValidationError: If the field ID does not match the expected transaction ID.
        """
        
        if data[0:2].strip() != "02":
            raise DataValidationError("Field ID for transaction must be '02'.")

        field_data = {
            "counter": data[2:8].strip(),
            "amount": data[8:20].strip(),
            "currency": data[20:23].strip(),
            "reserved": data[23:120].strip()
        }

        return field_data

    @staticmethod
    def parse_footer_data(data):
        """
        Parses raw string data to extract footer fields according to the fixed format.
        
        Args:
            data (str): Raw data string for the footer.
        
        Returns:
            dict: Parsed data dictionary for footer creation.
        
        Raises:
            DataValidationError: If the field ID does not match the expected footer ID.
        """
        
        if data[0:2].strip() != "03":
            raise DataValidationError("Field ID for footer must be '03'.")

        field_data = {
            "total_counter": data[2:8].strip(),
            "control_sum": data[8:20].strip(),
            "reserved": data[20:120].strip()
        }

        return field_data
