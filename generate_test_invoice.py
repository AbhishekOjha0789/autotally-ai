from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_invoice():
    # Create a clean white image simulating an invoice
    width, height = 800, 1000
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    # Draw sample invoice details
    draw.text((50, 50), "TAX INVOICE", fill="black")
    draw.text((50, 100), "Vendor: Acme Corp Supplies", fill="black")
    draw.text((50, 130), "Invoice Number: INV-2026-991", fill="black")
    draw.text((50, 160), "Date: 2026-08-21", fill="black")
    
    draw.text((50, 240), "Description", fill="gray")
    draw.text((600, 240), "Amount", fill="gray")
    draw.line([(50, 270), (750, 270)], fill="gray", width=1)
    
    draw.text((50, 300), "Cloud Server Hosting (1 Month)", fill="black")
    draw.text((600, 300), "12500.00", fill="black")
    
    draw.line([(50, 450), (750, 450)], fill="gray", width=1)
    draw.text((500, 480), "Subtotal: 12500.00", fill="black")
    draw.text((500, 510), "CGST (9%): 1125.00", fill="black")
    draw.text((500, 540), "SGST (9%): 1125.00", fill="black")
    draw.text((500, 580), "Total Amount: 14750.00", fill="black")
    
    file_path = "sample_test_invoice.png"
    image.save(file_path)
    print(f"Sample invoice generated successfully as '{file_path}'!")

if __name__ == "__main__":
    create_sample_invoice()