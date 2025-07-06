from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
import pytz

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["events"]

# Timezone for India
ist = pytz.timezone('Asia/Kolkata')

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")
    message = ""

    if event_type == "push":
        author = data["pusher"]["name"]
        branch = data["ref"].split("/")[-1]
        timestamp = datetime.now(ist).strftime("%d %B %Y - %I:%M %p IST")
        message = f'"{author}" pushed to "{branch}" on {timestamp}'

    elif event_type == "pull_request" and data["action"] == "opened":
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        timestamp = datetime.now(ist).strftime("%d %B %Y - %I:%M %p IST")
        message = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'

    elif event_type == "pull_request" and data["action"] == "closed" and data["pull_request"]["merged"]:
        author = data["pull_request"]["user"]["login"]
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        timestamp = datetime.now(ist).strftime("%d %B %Y - %I:%M %p IST")
        message = f'"{author}" merged branch "{from_branch}" to "{to_branch}" on {timestamp}'

    else:
        return jsonify({"status": "ignored"}), 200

    collection.insert_one({"message": message})
    return jsonify({"status": "stored"}), 200

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/events", methods=["GET"])
def get_events():
    messages = list(collection.find().sort("_id", -1))
    return jsonify([msg["message"] for msg in messages])

if __name__ == "__main__":
    app.run(debug=True)
