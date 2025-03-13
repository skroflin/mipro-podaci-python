import os
from PIL import Image
import shutil

# Definicija direktorija
current_directory = os.getcwd()
image_directory = os.path.join(current_directory, 'screenshots')
light_directory = os.path.join(image_directory, 'light-photos')
dark_directory = os.path.join(image_directory, 'dark-photos')

# Kreiranje direktorija ako ne postoje
os.makedirs(light_directory, exist_ok=True)
os.makedirs(dark_directory, exist_ok=True)

def calculate_white_percentage(image_path):
    """Funkcija koja računa postotak bijele boje na slici."""
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())
    
    white_pixels = sum(1 for pixel in pixels if pixel == (255, 255, 255))
    total_pixels = len(pixels)

    return (white_pixels / total_pixels) * 100 if total_pixels > 0 else 0

def classify_images(threshold=50):
    """Funkcija koja svrstava slike u light-photos ili dark-photos na temelju postotka bijele boje."""
    for file in os.listdir(image_directory):
        if file.endswith('.png'):
            image_path = os.path.join(image_directory, file)
            white_percentage = calculate_white_percentage(image_path)
            
            if white_percentage > threshold:
                shutil.move(image_path, os.path.join(light_directory, file))
                print(f"{file} premješten u light-photos/ ({white_percentage:.2f}% bijele boje)")
            else:
                shutil.move(image_path, os.path.join(dark_directory, file))
                print(f"{file} premješten u dark-photos/ ({white_percentage:.2f}% bijele boje)")

# Pokretanje klasifikacije slika
classify_images()
