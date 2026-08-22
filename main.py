from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
import os
import cv2
import numpy as np
import joblib
import fitz  # PyMuPDF
from dotenv import load_dotenv
from extractor import extract_invoice_data
from validator import validate_invoice_math
from builder import generate_tally_xml

load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="AutoTally AI API", version="1.0")

# Load the trained gatekeeper model at startup
MODEL_PATH = "receipt_gatekeeper_model.pkl"
try:
    gatekeeper_model = joblib.load(MODEL_PATH)
    print("Gatekeeper model loaded successfully into memory.")
except Exception as e:
    print(f"Warning: Could not load gatekeeper model from {MODEL_PATH}: {e}")
    gatekeeper_model = None

def extract_features(img_gray):
    """
    Extracts the exact structural contour features matching your training pipeline.
    """
    _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return [0, 0, 0, 0, 0]
        
    areas = []
    aspect_ratios = []
    solidity_vals = []
    
    for c in contours:
        area = cv2.contourArea(c)
        if area < 5: 
            continue
        areas.append(area)
        
        x, y, w, h = cv2.boundingRect(c)
        if h > 0:
            aspect_ratios.append(w / float(h))
            
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity_vals.append(area / float(hull_area))
            
    if not areas:
        return [0, 0, 0, 0, 0]
        
    return [
        len(areas),
        np.mean(areas),
        np.std(areas) if len(areas) > 1 else 0,
        np.mean(aspect_ratios) if aspect_ratios else 0,
        np.mean(solidity_vals) if solidity_vals else 0
    ]

def convert_bytes_to_cv2_gray(file_bytes: bytes, filename: str, mime_type: str) -> np.ndarray:
    """
    Converts raw file bytes (supporting both PDFs and standard images) 
    into a grayscale OpenCV image matrix.
    """
    if mime_type == "application/pdf" or filename.lower().endswith('.pdf'):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            return None
        page = doc[0]
        zoom = 2.0  # High-res rendering for sharper contour extraction
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        img_data = np.frombuffer(pix.samples, dtype=np.uint8)
        if pix.n == 4:
            img = img_data.reshape((pix.h, pix.w, 4))
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        elif pix.n == 3:
            img = img_data.reshape((pix.h, pix.w, 3))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            img = img_data.reshape((pix.h, pix.w))
        return img
    else:
        nparr = np.frombuffer(file_bytes, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

def is_valid_typed_invoice(file_bytes: bytes, filename: str, mime_type: str) -> bool:
    """Runs local ML structural gatekeeper check to block handwritten or invalid files for both images and PDFs."""
    if gatekeeper_model is None:
        return True  # Fallback if model isn't present
        
    try:
        img_gray = convert_bytes_to_cv2_gray(file_bytes, filename, mime_type)
        if img_gray is None:
            return False
            
        # Extract the exact contour features
        features = extract_features(img_gray)
        
        # Predict class (returns 'typed' or 'handwritten')
        prediction = gatekeeper_model.predict([features])[0]
        return prediction.lower() == "typed"
    except Exception:
        # If any preprocessing error occurs, let it pass through safely to Gemini
        return True

@app.post("/process-invoice", response_class=PlainTextResponse)
async def process_invoice(file: UploadFile = File(...), company_name: str = "My Company"):
    """
    Receives an inward purchase invoice (PDF or Image), runs ML structural gatekeeper, 
    parses via Gemini, runs math checks, and outputs a Tally-compliant XML file.
    """
    if not os.getenv("GEMINI_API_KEY"):
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is missing.")
    
    file_bytes = await file.read()
    mime_type = file.content_type or "application/pdf"
    filename = file.filename or "invoice.pdf"
    
    # Step 0: ML Gatekeeper Validation (Blocks handwriting/noise locally for both PDFs and images)
    if not is_valid_typed_invoice(file_bytes, filename, mime_type):
        raise HTTPException(
            status_code=400, 
            detail="Gatekeeper Blocked: Uploaded file appears to be handwritten or invalid noise. Please provide a structured digital invoice."
        )
    
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