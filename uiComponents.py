import streamlit as st
import pandas as pd

class UIComponents:
    """Renders clean, isolated sections of the dashboard metrics layout interface."""

    @staticmethod
    def render_kpi_cards(df_invoices: pd.DataFrame):
        """Displays high-level KPI scorecard panels at the top of the interface page."""
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Invoices Processed", len(df_invoices))
        with col2:
            st.metric("Total Invoiced Amount", f"QAR {df_invoices['total_amount'].sum():,.2f}")
        with col3:
            st.metric("Total Outstanding Balance", f"QAR {df_invoices['balance_due'].sum():,.2f}")
        with col4:
            overdue = len(df_invoices[df_invoices['invoice_status'].str.upper() == 'OVERDUE'])
            st.metric("Overdue Documents Count", overdue)

    @staticmethod
    def render_search_matrix(df_raw: pd.DataFrame, df_invoices: pd.DataFrame):
        """Builds granular drop-down lookups to view table data coordinate profiles."""
        st.subheader("Database Matrix Search")
        
        # Pull out a clean list of unique invoice numbers for the selector drop-down box
        options = ["All Documents"] + list(df_invoices['invoice_number'])
        selected = st.selectbox("Select Invoice Number to Filter Layout View Grid:", options)
        
        if selected == "All Documents":
            summary_columns = [
                'invoice_number', 'invoice_date', 'due_date', 
                'bill_to_name', 'total_amount', 'balance_due', 'invoice_status'
            ]
            
            # Filter and drop repeating rows so it displays exactly 1 unique summary row per invoice page!
            df_summary = df_invoices[summary_columns].copy()
            
            # 🧼 Visual Polish: Clean up technical column headers for the user
            df_summary.columns = [col.replace('_', ' ').upper() for col in df_summary.columns]
            
            st.dataframe(df_summary, use_container_width=True, hide_index=True)
            
        else:
            # Isolate the data matrix strictly matching the chosen invoice number sheet
            filtered = df_raw[df_raw['invoice_number'] == selected].copy()
            
            # Safe boundary check: if an empty list drops down, return gracefully
            if filtered.empty:
                st.info("No line items found for this record.")
                return
                
            # 🟢 FIXED LOGIC: Added '[0]' to correctly extract the first row as a clean Series map
            meta = filtered.iloc[0] 
            
            # Print quick invoice profile cards side-by-side
            c1, c2 = st.columns(2)
            c1.write(f"**Client Profile:** {meta['bill_to_name']}")
            c1.write(f"**Issue Date:** {meta['invoice_date']}")
            c2.write(f"**Status Field:** {meta['invoice_status']}")
            c2.write(f"**Due Date Tracker:** {meta['due_date']}")
            
            st.markdown("##### Itemized Invoice Line Items Table")
            
            # Render itemized matrix sub-table grid without any repeating headers or master columns
            items_grid = filtered[['description', 'quantity', 'unit_price', 'item_total']].copy()
            
            # 🧼 Visual Polish: Clean up sub-table headers as well
            items_grid.columns = [col.replace('_', ' ').upper() for col in items_grid.columns]
            
            st.dataframe(items_grid, use_container_width=True, hide_index=True)
