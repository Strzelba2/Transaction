class DataValidationError(Exception):
    """Exception raised for errors in the input data validation."""
    pass

class FileFormatError(Exception):
    """Exception raised for errors in the file format."""
    pass

class DataFactorError(Exception):
    """Exception raised for errors in the file format."""
    pass

class FileSaveError(Exception):
    """Exception raised for errors during file save operation."""
    pass