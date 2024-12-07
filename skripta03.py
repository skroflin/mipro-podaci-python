# -*- coding: utf-8 -*-
import os
import json
import codecs

output_dir = "analyzed-json"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def safe_get(audit_data, key):
    if "scoreDisplayMode" in audit_data and audit_data["scoreDisplayMode"] == "error":
        return "Error: " + str(audit_data.get('errorMessage', 'Unknown'))
    return audit_data.get(key, "Not available")

def extract_console_errors(audit_data):
    errors = []
    error_items = audit_data.get("details", {}).get("items", [])
    for item in error_items:
        errors.append({
            "source": item.get("source", "Unknown"),
            "description": item.get("description", "No description available"),
            "url": item.get("url", "No URL"),
            "line": item.get("lineNumber", "No line number"),
            "column": item.get("columnNumber", "No column number")
        })
    return errors

def use_json(enter_file):
    try:
        with codecs.open(enter_file, 'r', 'utf-8') as f:
            data = json.load(f)
        
        audits = data.get("audits", {})
        network_requests = audits.get("network-requests", {}).get("details", {}).get("items", [])
        console_errors = extract_console_errors(audits.get("errors-in-console", {}))
        
        obrada = {
            "HTTPS": safe_get(audits.get("is-on-https", {}), "score"),
            "HTTPS Protocols": [item.get("protocol", "Unknown") for item in network_requests],
            "Viewport": safe_get(audits.get("viewport", {}), "score"),
            "FCP (First Contentful Paint)": safe_get(audits.get("first-contentful-paint", {}), "displayValue"),
            "LCP (Largest Contentful Paint)": safe_get(audits.get("largest-contentful-paint", {}), "displayValue"),
            "Speed Index": safe_get(audits.get("speed-index", {}), "displayValue"),
            "Total Blocking Time (TBT)": safe_get(audits.get("total-blocking-time", {}), "displayValue"),
            "CLS (Cumulative Layout Shift)": safe_get(audits.get("cumulative-layout-shift", {}), "displayValue"),
            "TTI (Time to Interactive)": safe_get(audits.get("interactive", {}), "displayValue"),
            "FMP (First Meaningful Paint)": safe_get(audits.get("first-meaningful-paint", {}), "displayValue"),
            "Max Potential FID": safe_get(audits.get("max-potential-fid", {}), "displayValue"),
            "Server Response Time": safe_get(audits.get("server-response-time", {}), "numericValue"),
            "Number of Network Requests": len(network_requests),
            "JavaScript Execution Time": safe_get(audits.get("bootup-time", {}), "displayValue"),
            "Critical Request Chains": safe_get(audits.get("critical-request-chains", {}), "details"),
            "Console Errors": console_errors,
            "Responsive Images": safe_get(audits.get("image-size-responsive", {}), "score"),
            "Correct Aspect Ratio": safe_get(audits.get("image-aspect-ratio", {}), "score"),
            "Preload Key Requests": safe_get(audits.get("uses-rel-preload", {}), "details"),
            "Preconnect Suggestions": safe_get(audits.get("uses-rel-preconnect", {}), "details"),
        }
        
        exit_file = os.path.join(output_dir, os.path.basename(enter_file))
        with codecs.open(exit_file, 'w', 'utf-8') as f:
            json.dump(obrada, f, indent=4, ensure_ascii=False)
        
        print("File {} successfully analyzed.".format(enter_file))
    except Exception as e:
        print("Error while analyzing file {}: {}".format(enter_file, str(e)))

for datoteka in os.listdir("."):
    if datoteka.endswith(".json"):
        use_json(datoteka)
