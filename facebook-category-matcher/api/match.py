from http.server import BaseHTTPRequestHandler
import json
from rapidfuzz import process, fuzz
import os

CATEGORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'facebook_categories.json')
with open(CATEGORY_FILE) as f:
    FACEBOOK_CATEGORIES = json.load(f)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length)
            data = json.loads(post_data.decode('utf-8'))

            input_category = data.get("category", "").strip()

            if not input_category:
                self.send_error(400, "Missing 'category'")
                return

            match, score, _ = process.extractOne(input_category, FACEBOOK_CATEGORIES, scorer=fuzz.WRatio)

            confidence_level = (
                "High" if score >= 85 else
                "Medium" if score >= 70 else
                "Low"
            )

            response = {
                "original_category": input_category,
                "matched_category": match,
                "confidence_score": score,
                "confidence_level": confidence_level,
                "needs_manual_review": score < 70,
                "success": True
            }

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": str(e),
                "success": False
            }).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
