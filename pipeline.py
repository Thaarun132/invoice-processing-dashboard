import os
from dotenv import load_dotenv
from textExtraction import InvoiceExtractor
from databaseConnection import DatabaseConnection  # Your abstract base class template

# Load your hidden API key from the local .env file globally
load_dotenv()

class Pipeline:
    """Orchestrates the entire data flow from image extraction to database storage."""
    
    def __init__(self, db_manager: DatabaseConnection):
        """
        Initializes the pipeline with a specific database manager.
        Accepts any class that follows the DatabaseConnection abstract contract.
        """
        self.ai_reader = InvoiceExtractor()
        self.db_manager = db_manager

    def run_processing_pipeline(self, image_file: str):
        """
        Orchestrates the step-by-step pipeline execution flow.
        
        Args:
            image_file (str): The local disk path string pointing to the 
                              temporary image created from the dragged browser stream.
        """
        try:
            # Step 1: AI Reads the visual layout and text coordinates of the temp file
            raw_json_data = self.ai_reader.extract_data(image_file)
            
            # Step 2: Push the clean data payload straight into your active database manager
            self.db_manager.invoice_record(raw_json_data)
            print(f"[Pipeline] Successfully processed: {os.path.basename(image_file)}")
            
        except Exception as err:
            print(f"Orchestration Pipeline Error: {err}")
            raise err


# --- SECURE TERMINAL EXECUTION DOOR ---
if __name__ == "__main__":
    # Default image configurations have been scrubbed.
    # Direct terminal executions will now remind you to utilize the dashboard.
    print("The Document AI Pipeline is active and configured!")
    print("Launch your dashboard using 'streamlit run dashboard.py' to process dynamic drag-and-drop images.")

