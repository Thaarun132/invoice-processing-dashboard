import os
import re
import mysql.connector
from databaseConnection import DatabaseConnection  # Or whatever your base abstract class filename is

class MySQLDatabase(DatabaseConnection):
    """MySQL connector explicitly locked down to your custom port 330 architecture."""
    
    def __init__(self):
        self.host = "localhost"
        self.port = 330  #Force port 330 here
        self.user = "root"
        self.password = os.getenv("MYSQL_PASSWORD")  # Pulls securely from your hidden .env file
        self.database = "invoice_db"

    def _clean_numeric(self, val) -> float:
        """Helper to strip currency formats ('QAR 1,734.04' -> 1734.04)."""
        if not val: 
            return 0.0
        cleaned = re.sub(r'[^\d.]', '', str(val))
        return float(cleaned) if cleaned else 0.0


    def _get_connection(self):
        """Creates an authenticated connection object forcing your custom port."""
        if not self.password:
            raise ValueError("Error: MYSQL_PASSWORD is missing from your .env file setup!")
            
        # CRITICAL: We MUST explicitly pass port=self.port here so it doesn't default to 3306
        return mysql.connector.connect(
            host=self.host,
            port=self.port,  #THIS FIXES THE ERRNO 10061 ERROR
            user=self.user,
            password=self.password,
            database=self.database
        )

    def invoice_record(self, extracted_data: dict) -> None:
        inv_info = extracted_data["invoice_info"]
        bill_info = extracted_data["billing_details"]
        fin_summary = extracted_data["financial_summary"]
        
        db = self._get_connection()  # Using your port 330 connection helper
        cursor = db.cursor()
        
        try:
            # 🔍 Step 0: Check if this invoice number already exists in the database
            check_sql = "SELECT invoice_number FROM invoices WHERE invoice_number = %s"
            cursor.execute(check_sql, (inv_info["invoice_number"],))
            result = cursor.fetchone()
            
            if result:
                raise ValueError(f"Invoice '{inv_info['invoice_number']}' already exists in the system!")

            
            # # 1. Insert into Parent Table ('invoices') if it does NOT exist
            sql_parent = """
                INSERT INTO invoices (
                    invoice_number, invoice_date, due_date, po_number, payment_terms,
                    bill_to_name, bill_to_address, subtotal, shipping, total_amount,
                    balance_due, invoice_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            parent_vals = (
                inv_info["invoice_number"], inv_info["invoice_date"], inv_info["due_date"],
                inv_info["po_number"], inv_info["payment_terms"], bill_info["bill_to_name"],
                bill_info["bill_to_address"], self._clean_numeric(fin_summary["subtotal"]),
                self._clean_numeric(fin_summary["shipping"]), self._clean_numeric(fin_summary["total"]),
                self._clean_numeric(fin_summary["balance_due"]), inv_info["status"]
            )
            cursor.execute(sql_parent, parent_vals)
            
            # ... Followed by your child 'invoice_items' table insertion loop ...

            sql_child = """
                INSERT INTO invoice_items (invoice_number, description, quantity, unit_price, amount)
                VALUES (%s, %s, %s, %s, %s)
            """
            for item in extracted_data["line_items"]:
                qty_clean = int(re.sub(r'\D', '', item["quantity"])) if item["quantity"] else 1
                child_vals = (
                    inv_info["invoice_number"], item["description"], qty_clean,
                    self._clean_numeric(item["unit_price"]), self._clean_numeric(item["amount"])
                )
                cursor.execute(sql_child, child_vals)
            db.commit()
            print(f"[MySQL] Invoice {inv_info['invoice_number']} cleanly stored in database.")

        except Exception as error:
            db.rollback()
            print(f"[MySQL] Transaction Failure: Rolled back changes. Details: {error}")
            raise error
        finally:
            cursor.close()
            db.close()

    def fetch_data(self):
        """Fetches lines using our clean connection helper method."""
        import pandas as pd
        
        # Open connection utilizing port 330!
        db = self._get_connection()
        
        query = """
            SELECT 
                i.invoice_number, i.invoice_date, i.due_date, i.bill_to_name,
                i.total_amount, i.balance_due, i.invoice_status,
                it.description, it.quantity, it.unit_price, it.amount as item_total
            FROM invoices i
            LEFT JOIN invoice_items it ON i.invoice_number = it.invoice_number;
        """
        df = pd.read_sql(query, db)
        db.close()
        return df
