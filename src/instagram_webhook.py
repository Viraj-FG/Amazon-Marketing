# instagram_webhook.py - Webhook endpoint for Instagram verification
from flask import Flask, request, jsonify

app = Flask(__name__)
VERIFY_TOKEN = "viraj_openclaw_2026"

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Parse the query params
        verify_token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        # Verify the token
        if verify_token == VERIFY_TOKEN:
            return challenge, 200  # Respond with the challenge to fulfill verification
        else:
            return "Verification token mismatch", 403

    elif request.method == "POST":
        # Handle incoming webhook data
        data = request.get_json()
        print("Received webhook data:", data)
        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    # Run the server locally on port 5000
    app.run(host="0.0.0.0", port=5000)