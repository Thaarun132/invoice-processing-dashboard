import os
import streamlit as st
from mysqlDatabase import MySQLDatabase
from pipeline import Pipeline             # 🟢 CORRECTION: Import your master Pipeline class
from uiComponents import UIComponents

class InvoiceDashboardApp:
    """Coordinates data streams, browser uploads, AI parsing, and UI rendering modules."""
    
    def __init__(self):
        self.db = MySQLDatabase()
        
        # 🟢 CORRECTION: Pass your database into the master Pipeline tracking engine container!
        self.ai = Pipeline(db_manager=self.db)
        
        self.ui = UIComponents()

    def run(self):
        """Launches the Streamlit layout pipeline app instance."""
        st.set_page_config(page_title="Invoice Data Insights", page_icon="📊", layout="wide")
        st.title("Document Layout & Invoice Processing Dashboard")
        st.markdown("---")
        
        # 1. Browser Drag-and-Drop Image Uploader Canvas UI Block
        st.markdown("### Process New Document Invoice Image")
        uploaded_file = st.file_uploader(
            "Drag and drop or browse your invoice image (PNG, JPG, JPEG):", 
            type=["png", "jpg", "jpeg"]
        )
        
        # 🟢 NEW: Initialize a hidden flag memory tracker inside your browser's session state
        # This acts as an automated gatekeeper log
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()
        
        if uploaded_file is not None:
            # 🟢 NEW CORE CHECK: Only run if this specific filename has NOT been processed in this session yet
            if uploaded_file.name not in st.session_state.processed_files:
                with st.spinner("Gemini AI is analyzing document layout text and dimensions..."):
                    try:
                        image_bytes = uploaded_file.read()
                        temp_path = "temp_uploaded_invoice.png"
                        with open(temp_path, "wb") as f:
                            f.write(image_bytes)
                            
                        # Execute pipeline extraction directly from the temporary image bytes
                        self.ai.run_processing_pipeline(temp_path)
                        
                        st.success(f"Success! Invoice '{uploaded_file.name}' loaded into MySQL seamlessly.")
                        
                        # 🟢 LOCK THE GATE: Save this filename to session memory so it NEVER triggers on re-runs
                        st.session_state.processed_files.add(uploaded_file.name)
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                            
                        # Force a clean immediate UI refresh so the charts catch the new data instantly
                        st.rerun()
                            
                    except Exception as upload_err:
                        st.error(f"Insertion Blocked: {upload_err}")
                        # Even if it exists in DB, add it to session state to stop Gemini from re-running on filter changes
                        st.session_state.processed_files.add(uploaded_file.name)
                        
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
            else:
                # If it's already processed, we display a silent clean info message instead of re-running Gemini
                st.info(f"Document '{uploaded_file.name}' session check complete.")
                
        # 🟢 NEW EXTRA BONUS: If the user clicks the small 'x' to clear the uploader, 
        # reset our memory tracker so they can upload it clean next time!
        else:
            st.session_state.processed_files.clear()

        st.markdown("---")

        # 2. Render Existing Relational Database Layout Row Items
        try:
            # This data lookup fetches directly from your local MySQL on port 330
            df_raw = self.db.fetch_data()
            
            if df_raw.empty:
                st.warning("The database is currently empty. Drop an invoice image above to populate metrics.")
                return

            df_invoices = df_raw.drop_duplicates(subset=['invoice_number'])
            
            # Draw UI component blocks systematically from uiComponents.py
            self.ui.render_kpi_cards(df_invoices)
            st.markdown("---")
            self.ui.render_search_matrix(df_raw, df_invoices)
            
        except Exception as error:
            st.error(f"Failed to load layout interface dashboards from database: {error}")


if __name__ == "__main__":
    app = InvoiceDashboardApp()
    app.run()
