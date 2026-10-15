import json
import os
from google import genai
from google.genai import types

class InvoiceExtractor():
    #Handles all interactions with the Gemini API to extract images text.
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(
            api_key=self.api_key,
            vertexai=False,
            enterprise=False
        )
        self.model_name = "gemini-3.5-flash-lite"

    def _get_layout_prompt(self) -> str:
        #Returns the strict blueprint structure what gemini should do.
        return """
        Analyze this invoice image and extract all text content while maintaining its structured layout.
        Return the information in this strict JSON format:
        {
          "invoice_info": {
            "invoice_number": "string",
            "invoice_date": "YYYY-MM-DD",
            "due_date": "YYYY-MM-DD",
            "po_number": "string",
            "payment_terms": "string",
            "status": "string"
          },
          "billing_details": {
            "bill_to_name": "string",
            "bill_to_address": "string"
          },
          "line_items": [
            {
              "description": "string",
              "quantity": "string",
              "unit_price": "string",
              "amount": "string"
            }
          ],
          "financial_summary": {
            "subtotal": "string",
            "shipping": "string",
            "total": "string",
            "balance_due": "string"
          }
        }
        """

    def extract_data(self, image_path: str) -> dict:
        #Reads image binary data and queries Gemini for structural JSON layout.
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Could not locate image file at: {image_path}")
            
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                self._get_layout_prompt()
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
