import os
import random
from PIL import Image, ImageDraw, ImageFont

def setup_directories():
    os.makedirs("dataset/typed", exist_ok=True)
    os.makedirs("dataset/handwritten", exist_ok=True)

def get_random_font(size):
    possible_fonts = [
        "arial.ttf", "arialbd.ttf", "consola.ttf", "times.ttf", 
        "calibri.ttf", "cour.ttf", "segoeui.ttf", "verdana.ttf"
    ]
    font_dirs = [
        "C:\\Windows\\Fonts\\",
        "/usr/share/fonts/truetype/msttcorefonts/",
        "/usr/share/fonts/truetype/dejavu/"
    ]
    selected_font_name = random.choice(possible_fonts)
    for f_dir in font_dirs:
        full_path = os.path.join(f_dir, selected_font_name)
        if os.path.exists(full_path):
            try:
                return ImageFont.truetype(full_path, size)
            except Exception:
                continue
    return ImageFont.load_default()

def generate_massive_typed_dataset(count=1000):
    print(f"Generating {count} font-varied, scanned-style typed invoices for training...")
    vendors = ["Apex Global Ltd", "Nexus Tech Solutions", "Zenith Corp", "Pioneer Supplies", "Vertex Industries", "Alpha Logistics"]
    
    for i in range(count):
        width, height = random.choice([(800, 1000), (750, 1050), (820, 1100)])
        bg_color = random.choice(["white", "#fafafa", "#f2f2f2", "#fffdf0", "#eef2f5"])
        image = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Load fonts with varied sizes
        header_font = get_random_font(random.randint(18, 28))
        body_font = get_random_font(random.randint(12, 16))
        small_font = get_random_font(random.randint(10, 12))
        
        margin_x = random.randint(15, 140)
        margin_y = random.randint(15, 120)
        
        # Randomized Logo Variations
        logo_style = random.choice(["left", "center", "badge", "none"])
        if logo_style == "left":
            draw.rectangle([margin_x, margin_y, margin_x + 80, margin_y + 50], fill=random.choice(["#222", "#004080", "#444"]))
            draw.text((margin_x + 12, margin_y + 18), "CORP", fill="white", font=body_font)
            header_offset = 70
        elif logo_style == "center":
            draw.ellipse([width//2 - 40, margin_y, width//2 + 40, margin_y + 50], fill="#0056b3")
            header_offset = 70
        elif logo_style == "badge":
            draw.polygon([(width - margin_x - 70, margin_y), (width - margin_x, margin_y), (width - margin_x - 35, margin_y + 45)], fill="#333")
            header_offset = 60
        else:
            header_offset = 0

        # Simulate scanner artifacts & decorative curves
        if random.random() > 0.3:
            for _ in range(random.randint(1, 4)):
                rx1, ry1 = random.randint(0, width), random.randint(0, height)
                draw.line([(rx1, ry1), (rx1 + random.randint(-300, 300), ry1 + random.randint(-10, 10))], fill="#dcdcdc", width=random.randint(1, 3))
        
        if random.random() > 0.5:
            x0 = random.randint(0, width // 2)
            y0 = random.randint(0, height // 2)
            x1 = random.randint(width // 2, width)
            y1 = random.randint(height // 2, height)
            draw.arc([x0, y0, x1, y1], start=0, end=random.randint(90, 270), fill="#cccccc", width=2)

        # Invoice Header Details
        current_y = margin_y + header_offset
        draw.text((margin_x, current_y), random.choice(["TAX INVOICE", "INVOICE / BILL OF SUPPLY", "SALES RECEIPT", "COMMERCIAL INVOICE"]), fill="black", font=header_font)
        current_y += random.randint(25, 45)
        draw.text((margin_x, current_y), f"Vendor: {random.choice(vendors)}", fill="gray", font=body_font)
        current_y += random.randint(20, 30)
        draw.text((margin_x, current_y), f"Invoice #: INV-2026-{random.randint(10000, 99999)}", fill="black", font=body_font)
        current_y += random.randint(30, 50)
        
        # Table Grid Layout
        draw.text((margin_x, current_y), "Item Description", fill="black", font=body_font)
        draw.text((margin_x + int(width * 0.52), current_y), "Qty", fill="black", font=body_font)
        draw.text((margin_x + int(width * 0.70), current_y), "Amount", fill="black", font=body_font)
        current_y += 22
        draw.line([(margin_x, current_y), (width - margin_x, current_y)], fill="black", width=1)
        
        # Dynamic Item Rows
        current_y += 15
        num_items = random.randint(1, 7)
        subtotal = 0
        for item_idx in range(num_items):
            price = random.randint(150, 18000)
            subtotal += price
            draw.text((margin_x, current_y), f"Product SKU-{random.randint(100, 999)} Service Unit", fill="black", font=small_font)
            draw.text((margin_x + int(width * 0.52), current_y), str(random.randint(1, 4)), fill="black", font=small_font)
            draw.text((margin_x + int(width * 0.70), current_y), f"{price}.00", fill="black", font=small_font)
            current_y += random.randint(25, 35)
            
        # Totals Block
        current_y += 20
        draw.line([(margin_x + int(width * 0.3), current_y), (width - margin_x, current_y)], fill="gray", width=1)
        current_y += 12
        draw.text((margin_x + int(width * 0.3), current_y), f"Total Payable: {subtotal}.00", fill="black", font=body_font)

        image.save(f"dataset/typed/typed_invoice_{i+1}.png")

def generate_massive_handwritten_dataset(count=1000):
    print(f"Generating {count} chaotic handwritten & noise samples for training...")
    for i in range(count):
        width, height = random.choice([(800, 1000), (750, 1050)])
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        
        for _ in range(random.randint(50, 100)):
            x1, y1 = random.randint(10, width - 10), random.randint(10, height - 10)
            x2 = x1 + random.randint(-150, 150)
            y2 = y1 + random.randint(-50, 50)
            draw.line([(x1, y1), (x2, y2)], fill=random.choice(["#111111", "#000080", "#444444", "#8b0000"]), width=random.randint(1, 3))
            
        for _ in range(5):
            x0 = random.randint(50, width - 200)
            y0 = random.randint(50, height - 200)
            x1 = x0 + random.randint(100, 250)
            y1 = y0 + random.randint(100, 250)
            draw.arc([x0, y0, x1, y1], start=random.randint(0, 180), end=random.randint(180, 360), fill="black", width=2)
            
        draw.text((random.randint(40, 250), random.randint(100, 700)), "Random informal scratchpad notes / junk scribble", fill="black")
        
        image.save(f"dataset/handwritten/handwritten_note_{i+1}.png")

if __name__ == "__main__":
    setup_directories()
    generate_massive_typed_dataset(1000)
    generate_massive_handwritten_dataset(1000)
    print("Font-varied training dataset generation complete (2,000 files total)!")