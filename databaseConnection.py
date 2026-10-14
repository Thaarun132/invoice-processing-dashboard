from abc import ABC, abstractmethod
import pandas as pd

class DatabaseConnection(ABC):
    
    @abstractmethod
    def __init__(self):
        pass
    
    
    @abstractmethod
    def invoice_record(self, extracted_data: dict) -> None:
        """Insert invoice data into database"""
        pass

    @abstractmethod
    def fetch_data(self) -> pd.DataFrame:
        """Fetch the data from database"""
        pass