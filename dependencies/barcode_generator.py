import os
import barcode
from uuid import uuid4
from pathlib import Path
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

# Define the path where the barcodes will be stored
ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR  = "static"


def generate_valid_ean13() -> str:
    uuid_digits = str(uuid4().int)[:12]
    padded = uuid_digits.ljust(12, '0')[:12]
    total = 0
    for i, digit in enumerate(padded):
        num = int(digit)
        total += num * 3 if i % 2 == 1 else num
    check_digit = (10 - (total % 10)) % 10
    return padded + str(check_digit)


def write_to_image(product_name, image_path):
    """ Adds the product name below the barcode with a safe gap """
    full_image_path = image_path + ".png"

    if not os.path.exists(full_image_path):
        raise FileNotFoundError(f"Barcode image not found: {full_image_path}")

   
    image = Image.open(full_image_path)
    draw = ImageDraw.Draw(image)


    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    
    text_bbox = draw.textbbox((0, 0), product_name, font=font)
    text_width = text_bbox[2] - text_bbox[0]  
    text_height = text_bbox[3] - text_bbox[1]  

    new_height = image.height + text_height + 20

    new_image = Image.new("RGB", (image.width, new_height), "white")
    new_image.paste(image, (0, 0))  

    text_x = (image.width - text_width) // 2  
    text_y = image.height + 10 

    
    draw = ImageDraw.Draw(new_image)
    draw.text((text_x, text_y), product_name, font=font, fill="black")

   
    modified_path = image_path + "_labeled.png"
    new_image.save(modified_path)
    
    if os.path.exists(full_image_path):
        os.remove(full_image_path)
        
    return modified_path


def generate_barcode(product_name):
    """ Generates a barcode and overlays product name safely """
    barcode_num = generate_valid_ean13()
    ean = barcode.get('ean13', barcode_num, writer=ImageWriter())

    file_path = f"{ROOT_DIR}/{STATIC_DIR}/{barcode_num}"
    filename = ean.save(file_path)

    print(f"Generated barcode: {filename}")

    # Add product name below with safe spacing
    edited_image = write_to_image(product_name, file_path)
    return "/".join(edited_image.split("/")[-2:])
