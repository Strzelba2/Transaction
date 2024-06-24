from file_operations import FileOperations
import json
import logging
import os


class Config:
    def __init__(self):
        """
        Initializes the Config class by setting up the path for the lock configuration file and then loading
        the current lock configuration from the file. The lock configuration determines which fields in the data
        can be modified.
        """
        self.lock_config = {}
        self.lock_file_name = "lock_config.json"
        self.path_lock_file = os.path.join( FileOperations.current_directory, self.lock_file_name)
        self.load_lock_config()
        
    def load_lock_config(self):
        """
        Loads the lock configuration from a JSON file. This configuration specifies which fields in the data
        records are locked and cannot be edited directly by users.

        The function attempts to read the configuration from a file. If the file does not exist, it starts with
        an empty configuration, implying that no fields are initially locked. A warning is logged if the file is not found.
        """
        try:
            with open(self.path_lock_file, 'r') as f:
                self.lock_config = json.load(f)
            logging.info("Lock configuration loaded successfully.")
        except FileNotFoundError:
            self.lock_config = {}
            print("Lock configuration file not found. Starting with no locks.")
            logging.warning("Lock configuration file not found; proceeding without locks.")
            
    def save_lock_config(self):
        """
        Saves the current lock configuration to a JSON file. This is done to persist any changes made to the
        lock settings during the runtime of the application.

        The configuration is written back to the JSON file with an indentation of four spaces for readability.
        A log entry is generated to confirm the successful saving of the configuration.
        """
        with open(self.path_lock_file, 'w') as f:
            json.dump(self.lock_config, f, indent=4)   
        logging.info("Lock configuration saved successfully.")
    