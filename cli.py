import cmd
from file_operations import FileOperations
from configuration import Config
from validation import DataValidator
from data_factory import *
from exceptions import *
import logging
import json
import os

class CLI(cmd.Cmd):
    intro = 'Welcome to the data manager. Type help or ? to list commands.'
    prompt = '(data manager) '

    def __init__(self):
        super().__init__()
        self.file_ops = None
        self.filename = None
        self.config = Config()

    def do_lock(self, line):
        """Locks a specified field to prevent editing.
        Usage: lock [header|transaction|footer] field_name
        Example: lock transaction amount"""
        args = line.split()
        if len(args) != 2:
            print("Usage: lock [header|transaction|footer] field_name")
            logging.debug("Usage: lock [header|transaction|footer] field_name")
            return
        record_type, field_name = args
        if record_type in self.config.lock_config and field_name in self.config.lock_config[record_type]:
            self.config.lock_config[record_type][field_name] = True
            self.config.save_lock_config()
            print(f"Field '{field_name}' in '{record_type}' is now locked.")
            logging.info(f"Locked {field_name} in {record_type}.")
        else:
            print(f"Field '{field_name}' in '{record_type}' does not exist or is not configurable.")
            logging.error(f"Attempt to lock a non-existent or non-configurable field: {field_name} in {record_type}.")

    def do_unlock(self, line):
        """Unlocks a specified field to allow editing.
        Usage: unlock [header|transaction|footer] field_name
        Example: unlock transaction amount"""
        args = line.split()
        if len(args) != 2:
            print("Usage: unlock [header|transaction|footer] field_name")
            logging.debug("Usage: unlock [header|transaction|footer] field_name")
            return
        record_type, field_name = args
        if record_type in self.config.lock_config and field_name in self.config.lock_config[record_type]:
            self.config.lock_config[record_type][field_name] = False
            self.config.save_lock_config()
            print(f"Field '{field_name}' in '{record_type}' is now unlocked.")
            logging.info(f"Unlocked {field_name} in {record_type}.")
        else:
            print(f"Field '{field_name}' in '{record_type}' does not exist or is not configurable.")
            logging.error(f"Attempt to unlock a non-existent or non-configurable field: {field_name} in {record_type}.")

    def do_load(self, arg):
        """Load a file with the given filename.
        Usage: load <filename>
        Example: load example.txt"""
        self.filename = arg
        self.file_ops = FileOperations(self.filename)
        try:
            self.file_ops.read_file()
            print(f"File '{self.filename}' loaded successfully.")
            logging.info(f"File loaded: {self.filename}")
        except DataValidationError as e:
            error_msg = (f"Not correct data structure: {str(e)}."
                "Please correct the data structure and upload the file again:")
            logging.error(error_msg)
            print(error_msg)
        except DataFactorError as e:
            error_msg =f"Not valid data: {e}"
            logging.error(error_msg)
            print(error_msg)
            print("Please correct the data and upload the file again:")
        except FileFormatError as e:
            error_msg =f"Failed to load the file: {e}"
            logging.error(error_msg)
            print(error_msg)
            print("Please try loading a different file.")
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            print("Please check the file path and try loading again.")
        except PermissionError:
            error_msg = f"Permission denied: {self.filename}. Check your file permissions."
            print(error_msg)
            logging.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while loading file: {e}."
            print(error_msg)
            logging.error(error_msg)
            
    def do_get_field(self, line):
        """
        Usage:
            get_field record_type field_name [counter_value]
            Examples:
                get_field header name
                get_field footer total_counter
                get_field transaction amount 2
        
        Retrieves the value of a field from a specified record.
        For transactions, a counter value must be specified.
        """
        args = line.split()
        if len(args) < 2:
            print("Usage: get_field record_type field_name [counter_value]")
            logging.debug("Usage: get_field record_type field_name [counter_value]")
            return

        record_type, field_name = args[0], args[1]
        counter_value = args[2] if len(args) > 2 else None

        if record_type == "transaction" and not counter_value:
            print("Usage: get_field transaction field_name counter_value")
            logging.error("Usage: get_field transaction field_name counter_value")
            print("Counter value is required for transactions.")
            logging.error("Counter value is required for transactions.")
            return

        value = self.file_ops.get_field_value(record_type, field_name, counter_value)
        if isinstance(value, str):
            print(value)
        else:
            print(f"Error: Field not found or invalid parameters.{value}")
        
    def do_set_field(self, line):
        """Sets the value of a specified field in the loaded file if not locked.
        Usage: set_field [header|transaction|footer] field_name value [counter_value]
        Examples:
            set_field header name JohnDoe
            set_field transaction amount 123.45 1
        For transactions, a counter value must be specified."""

        args = line.split()
        if len(args) < 3:
            print("Usage: set_field [header|transaction|footer] field_name value")
            logging.debug("Usage: set_field [header|transaction|footer] field_name value")
            return

        record_type, field_name, value = args[0], args[1], args[2]
        
        try:
            if self.config.lock_config.get(record_type).get(field_name):
                print(f"Field '{field_name}' in '{record_type}' is locked and cannot be modified.")
                logging.error(f"Field '{field_name}' in '{record_type}' is locked and cannot be modified.")
                return
        except AttributeError:
            print(f"field '{field_name}'or object  '{record_type}'is not corrector lock_config.json does not exist ")
            logging.error(f"field '{field_name}'or object  '{record_type}'is not corrector lock_config.json does not exist ")
            return
        
        if (not self.file_ops):
            print("please upload the file for editing")
            logging.error("please upload the file for editing")
            return
        
        try:
            if record_type == "header" and hasattr(self.file_ops.header, field_name):
                try:
                    DataValidator.validate_field(self.file_ops.header, field_name, value)
                except DataValidationError as e:
                    logging.error(e)
                    print(e)
                    return
            elif  record_type == "transaction":
                
                counter_value = args[3] if len(args) > 3 else None
                if  not counter_value:
                    print("Usage: set_field transaction field_name counter_value")
                    print("Counter value is required for transactions.")
                    logging.error("Counter value is required for transactions.")
                    return
                formatted_counter_value = f"{counter_value:0>6}"
                logging.debug(f"formatted_counter_value: {formatted_counter_value}")
                
                transaction = next((t for t in self.file_ops.transactions if getattr(t, 'counter', '') == formatted_counter_value), None)
                if transaction:
                    old_amount = float(getattr(transaction, field_name))
                    new_amount = float(value)
                    try:
                        DataValidator.validate_field(transaction, field_name, new_amount)
                        control_sum = float(self.file_ops.footer.control_sum) - old_amount + new_amount
                        DataValidator.validate_field(self.file_ops.footer, "control_sum", control_sum)
                        print(f"Updated {field_name} to {new_amount} and recalculated control_sum to {control_sum}")
                    except DataValidationError as e:
                        print(e)
                        logging.error(e)
                        return
                else:
                    print("transaction with this number does not exist")
                    logging.error("transaction with this number does not exist")
                    return
                    
            elif record_type == "footer" and hasattr(self.file_ops.footer, field_name):
                try:
                    DataValidator.validate_field(self.file_ops.footer, field_name, value)
                except DataValidationError as e:
                    print(e)
                    logging.error(e)
                    return
            else:
                print("Invalid field or record type specified.")
                logging.error("Invalid field or record type specified.")
                return

            self.file_ops.save_file()

        except Exception as e:
            print(f"Error updating field: {str(e)}")
            logging.error(f"Error updating field: {str(e)}")

    def do_add_transaction(self, line):
        """
        Adds a transaction to the loaded file. The new transaction is validated and, if successful,
        the footer totals are updated accordingly.

        Usage:
            add_transaction amount 
        Examples:
            add_transaction 150.00 
            add_transaction 200

        Note:
            Sequential counter value is automatically used.
            The currency is according to the first transaction.
        """
        
        args = line.split()
        amount = args[0]
        
        if len(args) < 1:
            print("Usage: add_transaction amount ")
            logging.error("Usage: add_transaction amount ")
            return
        
        if (not self.file_ops):
            print("please upload the file for editing")
            logging.error("please upload the file for editing")
            return
        
        if not self.file_ops.currency:
            print("Currency not set. Load transactions or set currency first.")
            logging.error("Currency not set. Load transactions or set currency first.")
            return
        
        try:
            DataValidator.validate_type(amount, float)
        except DataValidationError as e:
            print(e)
            logging.error(e)
            return
        
        new_counter = f"{len(self.file_ops.transactions) + 1:06d}"
        
        transaction_data = {
            "counter": new_counter,
            "amount": float(amount),
            "currency": self.file_ops.currency,
            "reserved": " " * 96
        }
        
        try:
            new_transaction = DataFactory.create_transaction(transaction_data)
            self.file_ops.transactions.append(new_transaction)
            self.file_ops.update_footer(amount)
            self.file_ops.save_file()
            
        except DataFactorError as e:
            logging.error(f"Failed to add transaction: {e}")
            print(f"Failed to add transaction: {e}")
        except DataValidationError as e:
            logging.error(f"DataValidation Failed: {e}")
            print(f"DataValidation Failed: {e}")
    
    def do_quit(self, arg):
        """Exit the program."""
        print("Exiting the program.")
        return True

    def preloop(self):
        """Actions before entering the command loop."""
        if self.filename is None:
            print("No file is loaded. Please load a file to begin.")