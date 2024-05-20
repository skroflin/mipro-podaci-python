import base64
from PIL import Image
from io import BytesIO
import json
import os
import extcolors

current_directory = os.getcwd()
json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]

image_directory = os.path.join(current_directory, 'screenshots')
os.makedirs(image_directory, exist_ok=True)

color_json_directory = os.path.join(current_directory, 'color-json')
os.makedirs(color_json_directory, exist_ok=True)


def save_image(image_data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.b64decode(image_data.split(',')[1]))


def get_colors(img_path):
    img = Image.open(img_path).convert("RGBA")
    return extcolors.extract_from_image(img, tolerance=33, limit=10)


def create_image_entry(colors, file_name):
    total_pixels = colors[1]
    image_dict = {'file_name': file_name}
    image_colors = [{'colorCode': str(color), 'percent': round(count / total_pixels * 100)} for color, count in colors[0] if round(count / total_pixels * 100) >= 1]
    image_dict['img_colors'] = image_colors
    return image_dict


def process_images():
    collection = []

    for json_file in json_files:
        json_path = os.path.join(current_directory, json_file)

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'audits' in data and 'final-screenshot' in data['audits']:
            screenshot = data['audits']['final-screenshot']

            if 'details' in screenshot and 'data' in screenshot['details']:
                image_data = screenshot['details']['data']

                image_filename = os.path.join(image_directory, json_file.replace('.json', '_screenshot.png'))
                save_image(image_data, image_filename)
                print(f"Slika za datoteku '{json_file}' je spremljena kao '{image_filename}'")

                colors = get_colors(image_filename)
                file_dict = create_image_entry(colors, os.path.basename(image_filename))
                collection.append(file_dict)

                color_json_filename = os.path.join(color_json_directory, json_file.replace('.json', '_colors.json'))
                with open(color_json_filename, 'w', encoding='utf-8') as color_json_file:
                    json.dump(file_dict, color_json_file, ensure_ascii=False, indent=4)
                    print(f"Analiza boja za datoteku '{image_filename}' je spremljena kao '{color_json_filename}'")
            else:
                print(f"Nema slike za datoteku '{json_file}'")
        else:
            print(f"Nema slike za datoteku '{json_file}'")

    return collection

image_color_analysis = process_images()
for entry in image_color_analysis:
    print(entry)
