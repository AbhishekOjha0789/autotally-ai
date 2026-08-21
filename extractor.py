import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schemas import InvoiceData

load_dotenv()  # Load environment variables from .env file

# Initialize the Gemini client using the environment variable API key
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_invoice_data(file_bytes: bytes, mime_type: str = "application/pdf") -> InvoiceData:
    """
    Sends the invoice document (PDF or Image) to Gemini 3.6 Flash,
    enforces the Pydantic schema, and returns structured accounting data.
    """
    prompt = """
    Extract all structured accounting fields from this vendor invoice document precisely.
    Ensure:
    1. invoice_date is converted strictly to YYYYMMDD format (e.g., 20260821).
    2. Subtotal, CGST, SGST, IGST, and total_amount are exact decimal values.
    3. Separate CGST/SGST (for intra-state purchases) from IGST (for inter-state purchases).
    """
    
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=[
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InvoiceData,
            temperature=0.0
        )
    )
    
    # Parse and validate response directly against our Pydantic model
    return InvoiceData.model_validate_json(response.text)