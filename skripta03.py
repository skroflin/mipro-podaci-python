import os
import json

output_dir = "analyzed-json"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def safe_get(audit_data, key):
    if "scoreDisplayMode" in audit_data and audit_data["scoreDisplayMode"] == "error":
        return "Error: " + str(audit_data.get('errorMessage', 'Unknown'))
    return audit_data.get(key, "Not available")

def use_json(enter_file):
    try:
        with open(enter_file, 'r') as f:
            data = json.load(f)
        
        audits = data.get("audits", {})
        
        obrada = {
            "HTTPS": safe_get(audits.get("is-on-https", {}), "score"),
            "Viewport": safe_get(audits.get("viewport", {}), "score"),
            "FCP (First Contentful Paint)": safe_get(audits.get("first-contentful-paint", {}), "displayValue"),
            "LCP (Largest Contentful Paint)": safe_get(audits.get("largest-contentful-paint", {}), "displayValue"),
            "Speed Index": safe_get(audits.get("speed-index", {}), "displayValue"),
            "Total Blocking Time (TBT)": safe_get(audits.get("total-blocking-time", {}), "displayValue"),
            "CLS (Cumulative Layout Shift)": safe_get(audits.get("cumulative-layout-shift", {}), "displayValue"),
            "TTI (Time to Interactive)": safe_get(audits.get("interactive", {}), "displayValue"),
            "FMP (First Meaningful Paint)": safe_get(audits.get("first-meaningful-paint", {}), "displayValue"),
            "Max Potential FID": safe_get(audits.get("max-potential-fid", {}), "displayValue"),
            "Server Response Time": safe_get(audits.get("server-response-time", {}), "displayValue"),
            "JavaScript Execution Time": safe_get(audits.get("bootup-time", {}), "displayValue"),
            "Critical Request Chains": safe_get(audits.get("critical-request-chains", {}), "details"),
            "Number of Network Requests": safe_get(audits.get("network-requests", {}), "details"),
            "Console Errors": safe_get(audits.get("errors-in-console", {}), "details"),
            "Responsive Images": safe_get(audits.get("image-size-responsive", {}), "score"),
            "Correct Aspect Ratio": safe_get(audits.get("image-aspect-ratio", {}), "score"),
            "Preload Key Requests": safe_get(audits.get("uses-rel-preload", {}), "details"),
            "Preconnect Suggestions": safe_get(audits.get("uses-rel-preconnect", {}), "details"),
        }
        
        exit_file = os.path.join(output_dir, os.path.basename(enter_file))
        
        with open(exit_file, 'w') as f:
            json.dump(obrada, f, indent=4)
        
        print("File " + enter_file + " successfully analyzed.")
    except Exception as e:
        print("Error while analyzing file: " + enter_file + ": " + str(e))

for datoteka in os.listdir("."):
    if datoteka.endswith(".json"):
        use_json(datoteka)
