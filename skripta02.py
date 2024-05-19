import os
import json
import base64

current_directory = os.getcwd()
screenshot_directory = os.path.join(current_directory, 'screenshots')
os.makedirs(screenshot_directory, exist_ok=True)

json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]


def save_image(image_data, filename):
    with open(filename, "wb") as fh:
        fh.write(base64.decodebytes(image_data.encode()))


for json_file in json_files:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

        if 'audits' in data and 'final-screenshot' in data['audits']:
            screenshot = data['audits']['final-screenshot']

            if 'details' in screenshot and 'data' in screenshot['details']:
                image_data_inner = screenshot['details']['data']

                image_filename = os.path.join(screenshot_directory, json_file.replace('.json', '_screenshot.jpeg'))
                save_image(image_data_inner, image_filename)
                print(f"Slika za datoteku '{json_file}' je spremljena kao '{image_filename}'")
            else:
                print(f"Nema slike za datoteku '{json_file}'")
        else:
            print(f"Nema slike za datoteku '{json_file}'")
