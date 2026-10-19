import os
import streamlit as st
from databaseConnection import DatabaseConnection
from dotenv import load_dotenv
from pipeline import Pipeline
from uiComponents import UIComponents

load_dotenv()

class InvoiceDashboardApp:
    #Dashboard code
    
    def __init__(self, db_manager: DatabaseConnection):
        self.db = db_manager
        self.ai = Pipeline(db_manager=self.db)
        self.ui = UIComponents()

    def run(self):
        #Launches the Streamlit dashboard page
        st.set_page_config(page_title="Invoice Data Insights", page_icon="📊", layout="wide")
        st.title("Document Layout & Invoice Processing Dashboard")
        st.markdown("---")
        
        st.markdown("### Process New Document Invoice Image")
        uploaded_file = st.file_uploader(
            "Drag and drop or browse your invoice image (PNG, JPG, JPEG):", 
            type=["png", "jpg", "jpeg"]
        )
        
        #Initialise Session for upload image
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()
        
        if uploaded_file is not None:
            if uploaded_file.name not in st.session_state.processed_files:
                with st.spinner("Gemini AI is analyzing document layout text and dimensions..."):
                    try:
                        image_bytes = uploaded_file.read()
                        temp_path = "temp_uploaded_invoice.png"
                        with open(temp_path, "wb") as f:
                            f.write(image_bytes)
                            
                        self.ai.run_processing_pipeline(temp_path)
                        st.success(f"Success! Invoice '{uploaded_file.name}' loaded into MySQL seamlessly.")
                        st.session_state.processed_files.add(uploaded_file.name)
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                        st.rerun()
                            
                    except Exception as upload_err:
                        st.error(f"Insertion Blocked: {upload_err}")
                        st.session_state.processed_files.add(uploaded_file.name)
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            else:
                st.info(f"Document '{uploaded_file.name}' session check complete.")
                
        else:
            st.session_state.processed_files.clear()

        st.markdown("---")

        try:
            df_raw = self.db.fetch_data()
            
            if df_raw.empty:
                st.warning("The database is currently empty. Drop an invoice image above to populate metrics.")
                return

            df_invoices = df_raw.drop_duplicates(subset=['invoice_number'])
            self.ui.render_kpi_cards(df_invoices)
            st.markdown("---")
            self.ui.render_search_matrix(df_raw, df_invoices)
            
        except Exception as error:
            st.error(f"Failed to load layout interface dashboards from database: {error}")


if __name__ == "__main__":
    app = InvoiceDashboardApp()
    app.run()
