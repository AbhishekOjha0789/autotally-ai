from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
from extractor import extract_invoice_data
from validator import validate_invoice_math
from builder import generate_tally_xml

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="AutoTally AI API", version="1.0")

@app.post("/process-invoice", response_class=PlainTextResponse)
async def process_invoice(file: UploadFile = File(...), company_name: str = "My Company"):
    """
    Receives an inward purchase invoice, parses it via Gemini 3.6 Flash,
    runs math checks, and outputs a Tally-compliant XML file.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is missing.")
    
    file_bytes = await file.read()
    mime_type = file.content_type or "application/pdf"
    
    try:
        # Step 1: Extract data using Gemini
        invoice_data = extract_invoice_data(file_bytes, mime_type=mime_type)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract invoice data via AI: {str(e)}")
    
    # Step 2: Validate accounting math guardrail
    is_valid, message = validate_invoice_math(invoice_data)
    if not is_valid:
        raise HTTPException(status_code=422, detail=f"Math validation failed: {message}")
    
    # Step 3: Build Tally XML using builder module
    try:
        rendered_xml = generate_tally_xml(invoice_data, company_name=company_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return rendered_xml