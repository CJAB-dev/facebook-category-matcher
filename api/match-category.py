from flask import Flask, request, jsonify
from rapidfuzz import fuzz, process
import re
import json

app = Flask(__name__)

# Load Facebook categories
with open("facebook_categories.json") as f:
    FACEBOOK_CATEGORIES = json.load(f)

# Optional keywords for direct matching
CATEGORY_KEYWORDS = {
    "Electronics//Computers": ["laptop", "pc", "macbook", "computer"],
    "Antiques & Collectibles//Collectibles": ["collectible", "vintage", "memorabilia"],
    "Tools//Power Tools": ["drill", "saw", "tool", "wrench"],
    "Home & Garden//Furniture": ["sofa", "couch", "table", "chair"],
    "Sporting Goods//Exercise Equipment": ["treadmill", "weights", "dumbbell", "exercise bike"],
}

# Normalize input for better fuzzy matching
def normalize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s/]", "", text)  # Remove punctuation except slashes
    text = re.sub(r"\b(the|a|an|item|category|products?)\b", "", text)
    return text.strip()

@app.route("/api/match-category", methods=["POST"])
def match_category():
    try:
        data = request.get_json()
        user_input = data.get("category", "")

        if not user_input:
            return jsonify({"error": "Missing 'category' in request."}), 400

        normalized_input = normalize(user_input)

        # First check for keyword hit
        for category, keywords in CATEGORY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in normalized_input:
                    return jsonify({
                        "original": user_input,
                        "matched": category,
                        "confidence": 100,
                        "needs_review": False
                    })

        # Normalize all categories
        normalized_categories = {cat: normalize(cat) for cat in FACEBOOK_CATEGORIES}

        # Apply fuzzy matching
        best_match, score, _ = process.extractOne(
            normalized_input,
            normalized_categories.values(),
            scorer=fuzz.token_set_ratio
        )

        # Reverse lookup original category
        matched_category = next(orig for orig, norm in normalized_categories.items() if norm == best_match)

        return jsonify({
            "original": user_input,
            "matched": matched_category,
            "confidence": score,
            "needs_review": score < 80
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
