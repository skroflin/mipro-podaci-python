import os
import json

current_directory = os.getcwd()
output_directory = os.path.join(current_directory, 'web-data-json')

if not os.path.exists(output_directory):
    os.makedirs(output_directory)

json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]

def process_json_file(json_file):
    result = {}

    with open(json_file, 'r') as f:
        data = json.load(f)

    audits = data.get('audits', {})

    result['first-contentful-paint'] = audits.get('first-contentful-paint', {}).get('numericValue', None)
    result['largest-contentful-paint'] = audits.get('largest-contentful-paint', {}).get('numericValue', None)

    result['is-on-https'] = audits.get('is-on-https', {}).get('score', None)

    result['has-viewport'] = audits.get('viewport', {}).get('score', None)

    thumbnails = []
    if 'screenshot-thumbnails' in audits:
        items = audits['screenshot-thumbnails'].get('details', {}).get('items', [])
        for item in items:
            thumbnails.append({
                'timestamp': item.get('timestamp'),
                'data': item.get('data'),
            })
    result['screenshot-thumbnails'] = thumbnails

    return result

for json_file in json_files:
    file_path = os.path.join(current_directory, json_file)
    processed_data = process_json_file(file_path)

    output_file = os.path.join(output_directory, "{}_processed.json".format(os.path.splitext(json_file)[0]))
    with open(output_file, 'w') as f:
        json.dump(processed_data, f, indent=4, encoding='utf-8')
    print("Podaci iz {} spremljeni u {}".format(json_file, output_file)) 