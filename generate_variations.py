import os
import random
from PIL import Image, ImageDraw, ImageFont

def get_random_font(size):
    """
    Attempts to load various standard system fonts to introduce true font style variance.
    Falls back to default if custom fonts are unavailable.
    """
    possible_fonts = [
        "arial.ttf", "arialbd.ttf", "consola.ttf", "times.ttf", 
        "calibri.ttf", "cour.ttf", "segoeui.ttf", "verdana.ttf"
    ]
    
    # On Windows, fonts are typically stored in C:\Windows\Fonts
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
                
    # Fallback to default PIL font if system fonts aren't found
    return ImageFont.load_default()

def generate_massive_test_suite(total_images=1000, output_dir="test_variations"):
    typed_dir = os.path.join(output_dir, "typed")
    handwritten_dir = os.path.join(output_dir, "handwritten")
    os.makedirs(typed_dir, exist_ok=True)
    os.makedirs(handwritten_dir, exist_ok=True)
    
    print(f"Generating {total_images} extreme test files with diverse font styles, sizes, curves, and logos...")
    
    half_count = total_images // 2
    
    # 1. Generate Extreme Typed Invoices with Font Variations
    for i in range(half_count):
        width, height = random.choice([(800, 1000), (750, 1050), (850, 1150), (900, 1200)])
        bg_color = random.choice(["white", "#fafafa", "#f0f2f5", "#fffdf0", "#eef2f7"])
        image = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(image)
        
        # Load fonts with varied sizes for headers vs body text
        header_font = get_random_font(random.randint(18, 28))
        body_font = get_random_font(random.randint(12, 16))
        small_font = get_random_font(random.randint(10, 12))
        
        # Wildly shifting layout margins
        margin_x = random.randint(15, 140)
        margin_y = random.randint(15, 120)
        
        # Complex Logo & Badge Variations
        logo_style = random.choice(["rectangle_left", "circle_center", "polygon_right", "none"])
        if logo_style == "rectangle_left":
            draw.rectangle([margin_x, margin_y, margin_x + 80, margin_y + 50], fill=random.choice(["#222", "#004080", "#444"]))
            draw.text((margin_x + 12, margin_y + 18), "CORP", fill="white", font=body_font)
            header_offset = 70
        elif logo_style == "circle_center":
            draw.ellipse([width//2 - 40, margin_y, width//2 + 40, margin_y + 50], fill="#0056b3")
            header_offset = 70
        elif logo_style == "polygon_right":
            draw.polygon([(width - margin_x - 70, margin_y), (width - margin_x, margin_y), (width - margin_x - 35, margin_y + 45)], fill="#333")
            header_offset = 60
        else:
            header_offset = 0

        # Inject background watermarks, grid scan lines, and decorative curves
        if random.random() > 0.3:
            for _ in range(random.randint(1, 4)):
                rx1, ry1 = random.randint(0, width), random.randint(0, height)
                draw.line([(rx1, ry1), (rx1 + random.randint(-300, 300), ry1 + random.randint(-10, 10))], fill="#dcdcdc", width=random.randint(1, 3))
        
        # Add random decorative curved arcs
        if random.random() > 0.5:
            x0 = random.randint(0, width // 2)
            y0 = random.randint(0, height // 2)
            x1 = random.randint(width // 2, width)
            y1 = random.randint(height // 2, height)
            draw.arc([x0, y0, x1, y1], start=0, end=random.randint(90, 270), fill="#cccccc", width=2)

        # Invoice Header with position shifting and custom fonts
        current_y = margin_y + header_offset
        draw.text((margin_x, current_y), random.choice(["TAX INVOICE", "COMMERCIAL INVOICE", "PURCHASE RECEIPT", "BILL OF SUPPLY"]), fill="black", font=header_font)
        current_y += random.randint(25, 45)
        draw.text((margin_x, current_y), f"Invoice ID: INV-2026-{random.randint(10000, 99999)}", fill="gray", font=body_font)
        current_y += random.randint(30, 50)
        
        # Dynamic Table Columns
        draw.text((margin_x, current_y), "Description", fill="black", font=body_font)
        draw.text((margin_x + int(width * 0.52), current_y), "Qty", fill="black", font=body_font)
        draw.text((margin_x + int(width * 0.70), current_y), "Amount", fill="black", font=body_font)
        current_y += 22
        draw.line([(margin_x, current_y), (width - margin_x, current_y)], fill="black", width=1)
        
        # Dynamic Item Rows (1 to 7 items)
        current_y += 15
        num_items = random.randint(1, 7)
        subtotal = 0
        for item_idx in range(num_items):
            price = random.randint(150, 18000)
            subtotal += price
            draw.text((margin_x, current_y), f"Item SKU-{random.randint(100, 999)} Service Unit", fill="black", font=small_font)
            draw.text((margin_x + int(width * 0.52), current_y), str(random.randint(1, 4)), fill="black", font=small_font)
            draw.text((margin_x + int(width * 0.70), current_y), f"{price}.00", fill="black", font=small_font)
            current_y += random.randint(25, 35)
            
        # Totals Block
        current_y += 20
        draw.line([(margin_x + int(width * 0.3), current_y), (width - margin_x, current_y)], fill="gray", width=1)
        current_y += 12
        draw.text((margin_x + int(width * 0.3), current_y), f"Total Payable: {subtotal}.00", fill="black", font=body_font)
        
        image.save(os.path.join(typed_dir, f"extreme_typed_{i+1}.png"))

    # 2. Generate Extreme Handwritten & Noise Samples
    for i in range(half_count):
        width, height = random.choice([(800, 1000), (750, 1050)])
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        
        # Heavy messy handwriting scribbles and overlapping loops
        for _ in range(random.randint(50, 100)):
            x1, y1 = random.randint(10, width - 10), random.randint(10, height - 10)
            x2 = x1 + random.randint(-150, 150)
            y2 = y1 + random.randint(-50, 50)
            draw.line([(x1, y1), (x2, y2)], fill=random.choice(["#111111", "#000088", "#555555", "#aa0000"]), width=random.randint(1, 3))
            
        # Random chaotic arcs with safe bounds
        for _ in range(5):
            x0 = random.randint(50, width - 200)
            y0 = random.randint(50, height - 200)
            x1 = x0 + random.randint(100, 250)
            y1 = y0 + random.randint(100, 250)
            draw.arc([x0, y0, x1, y1], start=random.randint(0, 180), end=random.randint(180, 360), fill="black", width=2)
            
        draw.text((random.randint(40, 250), random.randint(100, 700)), "Random informal scratchpad notes / junk scribble", fill="black")
        
        image.save(os.path.join(handwritten_dir, f"extreme_handwritten_{i+1}.png"))

    print(f"Successfully generated {total_images} font-varied test files inside '{output_dir}/'!")

if __name__ == "__main__":
    generate_massive_test_suite(1000)