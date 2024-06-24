from dataclasses import dataclass, field
from validation import DataValidator

@dataclass
class Header:
    """
    Represents the header section of a fixed-width file. This section includes essential
    identification fields such as name, surname, patronymic, and address, each with specified
    width, ensuring consistent record formatting.
    """
    _field_id: str = field(default="01", init=False)
    name: str = field(default=""*28, metadata={"fixed_width": 28, "type": str})
    surname: str = field(default=""*30, metadata={"fixed_width": 30, "type": str})
    patronymic: str = field(default=""*30, metadata={"fixed_width": 30, "type": str})
    address: str = field(default=""*30, metadata={"fixed_width": 30, "type": str})
    
    def __post_init__(self):
        DataValidator.validate_dataclass(self)
          
    @property
    def field_id(self):
        return self._field_id

    @field_id.setter
    def field_id(self, value):
        raise AttributeError("Cannot modify field_id")
    
    def to_fixed_width_string(self):
        """
        Formats the header data into a fixed-width string according to the specified widths.
        """
        return f"{self.field_id}{self.name}{self.surname}{self.patronymic}{self.address}"

@dataclass
class Transaction:
    """
    Represents an individual transaction record in a fixed-width file. Includes transaction
    counter, amount, currency, and reserved space, all formatted to specific widths to maintain
    file consistency.
    """
    _field_id: str = field(default="02", init=False)
    counter: str = field(default=""*6, metadata={"fixed_width": 6, "type": str})
    amount: str = field(default="0.00".rjust(12, '0'), metadata={"fixed_width": 12, "type": float})
    currency: str = field(default=""*3, metadata={"fixed_width": 3, "type": str})
    reserved: str = field(default=" " * 97, metadata={"fixed_width": 97, "type": str})
    
    def __post_init__(self):
        DataValidator.validate_dataclass(self)
        
    @property
    def field_id(self):
        return self._field_id

    @field_id.setter
    def field_id(self, value):
        raise AttributeError("Cannot modify field_id")
    
    def to_fixed_width_string(self):
        """
        Formats the transaction data into a fixed-width string. Ensures alignment of all
        transaction records in the file.
        """
        return f"{self.field_id}{self.counter}{self.amount}{self.currency}{self.reserved}"

@dataclass
class Footer:
    """
    Represents the footer section of a fixed-width file, summarizing the transactions. It includes
    the total count of transactions and the cumulative sum of all transaction amounts, ensuring
    both are formatted to fixed widths for file integrity checks.
    """
    _field_id: str = field(default="03", init=False)
    total_counter: str = field(default="1".rjust(6, '0'), metadata={"fixed_width": 6, "type": int})
    control_sum: str = field(default="0.00".rjust(12, '0'), metadata={"fixed_width": 12, "type": float})
    reserved: str = field(default=" " * 100, metadata={"fixed_width": 100, "type": str})
    
    def __post_init__(self):
        DataValidator.validate_dataclass(self)
        
    @property
    def field_id(self):
        return self._field_id

    @field_id.setter
    def field_id(self, value):
        raise AttributeError("Cannot modify field_id")
    
    def to_fixed_width_string(self):
        """
        Converts the footer information into a fixed-width string, crucial for end-of-file
        validation processes.
        """
        return f"{self.field_id}{self.total_counter}{self.control_sum}{self.reserved}"