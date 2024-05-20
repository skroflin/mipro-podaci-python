import base64
from PIL import Image
import json
import os
import extcolors
import webcolors

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

def closest_color(requested_color):
    min_colors = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    return min_colors[min(min_colors.keys())]

def create_image_entry(colors, file_name, site_id):
    total_pixels = colors[1]
    image_colors = []
    for color, count in colors[0]:
        percent = round(count / total_pixels * 100)
        if percent >= 1:
            color_name = closest_color(color)
            rgb_color = ','.join(map(str, color))
            color_name = closest_color(color)
            image_colors.append({
                'colorCode': rgb_color,
                'colorName': color_name,
                'percent': percent
            })

    return {
        'site_id': site_id,
        'file_name': file_name,
        'img_colors': image_colors
    }

def process_images():
    all_site_data = []

    for json_file in json_files:
        json_path = os.path.join(current_directory, json_file)

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        site_id = int(os.path.splitext(json_file)[0])

        if 'audits' in data and 'final-screenshot' in data['audits']:
            screenshot = data['audits']['final-screenshot']

            if 'details' in screenshot and 'data' in screenshot['details']:
                image_data = screenshot['details']['data']

                image_filename = os.path.join(image_directory, json_file.replace('.json', '_screenshot.png'))
                save_image(image_data, image_filename)

                colors = get_colors(image_filename)
                image_entry = create_image_entry(colors, os.path.basename(image_filename), site_id)
                all_site_data.append(image_entry)

    return all_site_data

site_color_analysis = process_images()
output_filename = os.path.join(color_json_directory, 'all_sites_color_analysis.json')
with open(output_filename, 'w', encoding='utf-8') as output_file:
    json.dump(site_color_analysis, output_file, ensure_ascii=False, indent=4)
    print(f"Svi rezultati analize boja su spremljeni u '{output_filename}'")