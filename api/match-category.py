from http.server import BaseHTTPRequestHandler
import json
from rapidfuzz import process, fuzz

FACEBOOK_CATEGORIES = [
    "Electronics//TVs",
    "Home & Garden//Furniture",
    "Antiques & Collectibles//Antique & Collectible Furniture"
]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        data = json.loads(body)

        input_category = data.get("category", "")
        match, score, _ = process.extractOne(
            input_category,
            FACEBOOK_CATEGORIES,
            scorer=fuzz.WRatio
        )

        response = {
            "original": input_category,
            "matched": match,
            "confidence": score,
            "needs_review": score < 80
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
