import os
import json
import codecs

current_directory = os.getcwd()
output_directory = os.path.join(current_directory, 'web-details-json')
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]

def process_json_file(json_file):
    result = {}

    with codecs.open(json_file, 'r', 'utf-8') as f:
        data = json.load(f)

    audits = data.get('audits', {})
    categories = data.get('categories', {})
    network_data = data.get('network-requests', {}).get('details', {}).get('items', [])
    resources = audits.get('network-requests', {}).get('details', {}).get('items', [])

    result['cumulative-layout-shift'] = audits.get('cumulative-layout-shift', {}).get('numericValue', None)
    result['total-blocking-time'] = audits.get('total-blocking-time', {}).get('numericValue', None)
    result['speed-index'] = audits.get('speed-index', {}).get('numericValue', None)
    result['first-contentful-paint'] = audits.get('first-contentful-paint', {}).get('numericValue', None)
    result['largest-contentful-paint'] = audits.get('largest-contentful-paint', {}).get('numericValue', None)
    result['page-load-time'] = audits.get('interactive', {}).get('numericValue', None)
    result['memory-usage'] = audits.get('main-thread-tasks', {}).get('details', {}).get('summary', {}).get('totalBytes', None)
    result['cpu-usage'] = audits.get('main-thread-tasks', {}).get('details', {}).get('summary', {}).get('totalTasks', None)

    result['first-paint'] = audits.get('first-paint', {}).get('numericValue', None)
    result['first-meaningful-paint'] = audits.get('first-meaningful-paint', {}).get('numericValue', None)
    result['time-to-interactive'] = audits.get('interactive', {}).get('numericValue', None)

    result['long-tasks'] = len(audits.get('long-tasks', {}).get('details', {}).get('items', []))
    result['javascript-load-time'] = sum(item.get('duration', 0) for item in resources if item.get('type') == 'Script')
    result['css-load-time'] = sum(item.get('duration', 0) for item in resources if item.get('type') == 'Stylesheet')
    result['image-optimization-opportunities'] = [
        {
            'url': item.get('url'),
            'wastedBytes': item.get('wastedBytes')
        }
        for item in audits.get('uses-optimized-images', {}).get('details', {}).get('items', [])
    ]

    result['cdn-utilization'] = any('cdn' in item.get('url', '').lower() for item in resources)
    result['server-response-time'] = audits.get('server-response-time', {}).get('numericValue', None)

    result['render-blocking-resources'] = [
        item.get('url') for item in audits.get('render-blocking-resources', {}).get('details', {}).get('items', [])
    ]

    result['idle-cpu-time'] = audits.get('diagnostics', {}).get('details', {}).get('items', [{}])[0].get('totalIdleTime', None)

    result['seo-checks'] = {
        'alt-tags': audits.get('image-alt', {}).get('score', None),
        'robots-txt': audits.get('robots-txt', {}).get('score', None),
        'sitemap': audits.get('sitemap', {}).get('score', None)
    }

    result['accessibility-checks'] = {
        'contrast': audits.get('color-contrast', {}).get('score', None),
        'aria-labels': audits.get('aria-labels', {}).get('score', None)
    }

    result['http-requests'] = len(network_data)
    result['http-request-duration'] = sum(item.get('duration', 0) for item in network_data)
    result['http-requests-per-second'] = (
        result['http-requests'] / (result['http-request-duration'] / 1000)
        if result['http-request-duration'] else None
    )

    thumbnails = []
    screenshot_data = audits.get('screenshot-thumbnails', {}).get('details', {}).get('items', [])
    for item in screenshot_data:
        thumbnails.append({
            'timestamp': item.get('timestamp'),
            'data': item.get('data'),
        })
    result['screenshot-thumbnails'] = thumbnails

    meta_description = audits.get('meta-description', {}).get('details', {}).get('items', [])
    meta_title = audits.get('meta-title', {}).get('details', {}).get('items', [])
    canonical_link = audits.get('canonical', {}).get('details', {}).get('items', [])

    result['seo-meta'] = {
        'description': meta_description[0].get('value') if meta_description else None,
        'title': meta_title[0].get('value') if meta_title else None,
        'canonical': canonical_link[0].get('url') if canonical_link else None
    }

    heading_structure = audits.get('heading-order', {}).get('details', {}).get('items', [])
    result['seo-heading-structure'] = heading_structure

    structured_data = audits.get('structured-data', {}).get('details', {}).get('items', [])
    result['seo-structured-data'] = structured_data

    indexability = audits.get('robots-txt', {}).get('score', None)
    result['seo-indexability'] = indexability

    keyboard_navigation = audits.get('keyboard-navigation', {}).get('score', None)
    result['accessibility-checks']['keyboard-navigation'] = keyboard_navigation

    is_https = audits.get('is-on-https', {}).get('score', None)
    result['best-practices'] = {
        'is-https': is_https
    }

    cache_control = audits.get('uses-long-cache-ttl', {}).get('score', None)
    expires_header = audits.get('uses-expires', {}).get('score', None)
    result['best-practices']['cache-control'] = cache_control
    result['best-practices']['expires-header'] = expires_header

    external_scripts = audits.get('uses-external-scripts', {}).get('details', {}).get('items', [])
    result['best-practices']['external-scripts'] = [script.get('url') for script in external_scripts]

    csp = audits.get('content-security-policy', {}).get('score', None)
    result['security-compliance'] = {
        'content-security-policy': csp
    }

    cookies = audits.get('cookies', {}).get('details', {}).get('items', [])
    result['security-compliance']['cookies'] = [
        {
            'name': cookie.get('name'),
            'secure': cookie.get('secure'),
            'httpOnly': cookie.get('httpOnly'),
            'sameSite': cookie.get('sameSite')
        }
        for cookie in cookies
    ]

    gdpr_compliance = audits.get('gdpr', {}).get('score', None)
    result['security-compliance']['gdpr-compliance'] = gdpr_compliance

    first_input_delay = audits.get('first-input-delay', {}).get('numericValue', None)
    result['usability-behavior'] = {
        'first-input-delay': first_input_delay
    }

    return result

for json_file in json_files:
    file_path = os.path.join(current_directory, json_file)
    processed_data = process_json_file(file_path)

    output_file = os.path.join(output_directory, "{}_details.json".format(os.path.splitext(json_file)[0]))
    with codecs.open(output_file, 'w', 'utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)

    print("Procesuirani {} -> Spremljeni u {}".format(json_file, output_file))
