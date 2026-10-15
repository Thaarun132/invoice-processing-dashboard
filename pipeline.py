from textExtraction import InvoiceExtractor
from databaseConnection import DatabaseConnection

class Pipeline:
    #Orchestrates the entire data flow from image extraction to database storage.
    
    def __init__(self, db_manager: DatabaseConnection):
        self.ai_reader = InvoiceExtractor()
        self.db_manager = db_manager

    def run_processing_pipeline(self, image_file: str):
        #Orchestrates the step-by-step pipeline execution flow.
        try:
            raw_json_data = self.ai_reader.extract_data(image_file)
            self.db_manager.invoice_record(raw_json_data)
            
        except Exception as err:
            raise err