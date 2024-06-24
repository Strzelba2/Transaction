import os
import logging
from exceptions import DataValidationError

class DataValidator:
    """
    Provides methods for validating types, lengths, and structural integrity of fields 
    in dataclass instances, ensuring they conform to the expected formats. 
    Used primarily to ensure data consistency across fixed-width formatted files.
    """
    ALLOWED_CURRENCIES = {'USD', 'EUR', 'GBP', 'PLN'}
    
    @staticmethod
    def validate_type(value, expected_type):
        """
        Validates that the value is of the expected type. This includes type checks and 
        conversions for numeric types.
        
        Args:
            value: The value to be validated.
            expected_type: The type the value is expected to conform to.
        
        Raises:
            DataValidationError: If the value does not match the expected type.
        """
        logging.debug(f"Starting validate_type with value='{value}' and expected_type={expected_type}")
        if expected_type is float:
            try:
                logging.debug(value)
                if isinstance(float(value), expected_type):
                    logging.debug(f"Value '{value}' is a  number.")
                    if (float(value)<0):
                        raise ValueError("The numbers cannot be negative")
                    return value
            except ValueError as e:
                logging.error(f"Type validation error: {e}")
                raise DataValidationError(f"Expected a float, got {type(value)}: {e}") 
        elif expected_type is int:
            try:
                logging.debug(value)
                if isinstance(int(value), expected_type):
                    logging.debug(f"Value '{value}' is a  number.")
                    if (int(value)<0):
                        raise ValueError("The numbers cannot be negative")
                    return value
            except ValueError as e:
                logging.error(f"Type validation error: {e}")
                raise DataValidationError(f"Expected an int, got {type(value)}: {e}")
        
        if not isinstance(value, expected_type):
            logging.error(f"Type mismatch: Expected {expected_type}, got {type(value)}")
            raise DataValidationError(f"Expected value type {expected_type}, but got {type(value)}.")
        return value

    @staticmethod
    def validate_fixed_width(value, width):
        """
        Ensures the value fits within the specified width. Formats numeric values with 
        leading zeros or space-padding as necessary. Also rounds floats to two decimal places.

        Args:
            value: The value to be formatted and validated.
            width: The required fixed width for the value.
        
        Raises:
            DataValidationError: If the formatted value exceeds the specified width.
        """
        logging.debug(f"Starting validate_fixed_width with value='{value}' and width={width}")
        
        if isinstance(value, int):
            # Formatting an integer with leading zeros
            formatted_value = f"{value:0{width}d}"
            logging.debug(f"formatted_value='{formatted_value}'")
        elif isinstance(value, float):
            # Formatting a floating point number with two decimal places
            formatted_value = f"{value:0{width}.2f}"
            logging.debug(f"formatted_value='{formatted_value}'")
        else:
            # Format strings by adding spaces if they are too short
            formatted_value = f"{value}".rjust(width)
            logging.debug(f"{formatted_value}:{len(formatted_value)}")

        # Checking that the formatted value does not exceed the set width
        if len(formatted_value) > width:
            error_msg = f"Formatted value '{formatted_value}' exceeds maximum width of {width}."
            logging.error(error_msg)
            raise DataValidationError(error_msg)

        return formatted_value
    
    @staticmethod
    def validate_file_exists(filename):
        """
        Checks if the specified file exists on the file system. This is used to prevent 
        operations on non-existing files which could lead to errors.
        
        Args:
            filename: The path of the file to check.
        
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        logging.debug(f"validate_file_exists")
        if not os.path.exists(filename):
            error_msg = f"No file found at the specified path: {filename}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)
        
    @staticmethod
    def validate_file_structure(lines):
        """
        Validates the overall structure of the file from the provided lines, ensuring 
        it includes a header, a valid number of transactions, and a footer. Checks that 
        each line adheres to the expected length of 120 characters.
        
        Args:
            lines: List of lines from the file to be validated.
        
        Raises:
            DataValidationError: If the file structure is incorrect or any line does not meet the length requirement.
        """
        logging.debug(f"validate_file_structure")
        if len(lines) < 3:
            error_msg = "File must contain at least one header, one transaction, and one footer."
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        
        logging.debug(f"checking line length")
        for line in lines:
            logging.debug(len(line.rstrip('\r\n')))
        if any(len(line.rstrip('\r\n')) != 120 for line in lines):
            error_msg = "Each line must be exactly 120 characters long."
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        
        logging.debug(f"checking headers")

        header, footer = lines[0], lines[-1]
        if not header.startswith("01") or not footer.startswith("03"):
            error_msg = "File must start with a header and end with a footer."
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        
        logging.debug(f"checking amount of transactions")

        transaction_lines = lines[1:-1]
        
        if any(not transaction.startswith("02") for transaction in transaction_lines):
            error_msg = "Each transaction must start with 02 id"
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        
        if not (1 <= len(transaction_lines) <= 20000):
            error_msg = "The number of transaction records must be between 1 and 20,000."
            logging.error(error_msg)
            raise DataValidationError(error_msg)
        logging.info("File structure validated successfully.")

    @classmethod
    def validate_dataclass(cls, instance):
        """
        Validates all fields in a dataclass instance using metadata for fixed width and type. 
        Applies width and type validation for each field based on its metadata settings.
        
        Args:
            instance: The dataclass instance to validate.
        
        Raises:
            DataValidationError: If any field does not conform to its specified type or width.
        """
        logging.debug(f"Starting validate_dataclass for instance of {instance.__class__.__name__}")
        
        for field in instance.__dataclass_fields__.values():
            logging.debug(f"field: name: {field.name}")
            if field.name == "_field_id":
                continue
            value = getattr(instance, field.name)
            expected_type = field.metadata['type']
            fixed_width = field.metadata['fixed_width']
            logging.debug(f"validate_dataclass: value: {value}, expected_type:{expected_type}, fixed_widthŁ{fixed_width} ")
            cls.validate_type(value, expected_type)
            formatted_value = cls.validate_fixed_width(value, fixed_width)
            setattr(instance, field.name, formatted_value)
            logging.debug(f"Field '{field.name}' set to '{formatted_value}'")
            
    @classmethod
    def validate_field(cls, instance ,field_name, value):
        """
        Validates a single field of a dataclass instance based on its metadata for type and width.

        Args:
            instance: The dataclass instance containing the field.
            field_name: The name of the field to validate.
            value: The new value to set for the field.

        Raises:
            DataValidationError: If the field does not conform to its specified type or width.
        """
  
        instance_field = next(field for field in instance.__dataclass_fields__.values() if field.name == field_name)
        
        expected_type = instance_field.metadata['type']
        fixed_width = instance_field.metadata['fixed_width']
        
        logging.debug(f"validate_dataclass: value: {value}, expected_type:{expected_type}, fixed_widthŁ{fixed_width} ")
        
        formatted_value =cls.validate_type(value, expected_type)
        formatted_value = cls.validate_fixed_width(value, fixed_width)
        
        setattr(instance, instance_field.name, formatted_value)
        logging.debug(f"Field '{instance_field.name}' set to '{formatted_value}'")