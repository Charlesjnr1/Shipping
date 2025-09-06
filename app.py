from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# JSON persistence
DATA_FILE = "tracking.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(tracking_data, f, indent=4)

# Load tracking data from file (or initialize with default)
tracking_data = load_data()

if not tracking_data:
    tracking_data = {
        "ESLD174601": {
            "status": "In Transit",
            "location": "Cyd-cheresse Hill",
            "progress": 80,
            "progressStage": 4,
            "balance_due": 0.00,
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "history": [
                {"label": "Picked Up", "location": "Buckhead Loop NE, ATL", "done": True},
                {"label": "In Transit", "location": "Rogell Drive, MI", "done": True},
                {"label": "Mid-Route Checkpoint", "location": "Detroit,US", "done": True},
                {"label": "Border Clearance", "location": "Metropolitan Wayne county Airport", "done": False, "pending_reason": ""},
                {"label": "Out for Delivery", "location": "Cyd-cheresse Hill,US", "done": False},
                {"label": "Delivered", "location": "pending", "done": False}
            ]
        }
    }
    save_data()

# Admin credentials
USERS = {
    "admin": {"password": "password", "role": "admin"},
    "George": {"password": "George@123", "role": "viewer"},
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/track", methods=["POST"])
def track():
    tracking_id = request.json.get("trackingId", "").strip().upper()
    data = tracking_data.get(tracking_id)

    if data:
        return jsonify({
            "found": True,
            "trackingId": tracking_id,
            "status": data["status"],
            "location": data["location"],
            "progress": data["progress"],
            "progressStage": data["progressStage"],
            "balance_due": data.get("balance_due", 0),
            "history": data.get("history", []),
            "updated": data.get("updated")
        })
    else:
        return jsonify({"found": False, "message": f"Tracking ID '{tracking_id}' not found."})

@app.before_request
def enforce_https_in_production():
    if request.headers.get('X-Forwarded-Proto', 'http') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = USERS.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid credentials")
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if "username" not in session:
        return redirect(url_for("admin_login"))

    if session.get("role") == "viewer":
        return render_template("admin_readonly.html", data=tracking_data)

    return render_template("admin_dashboard.html", data=tracking_data)

@app.route("/admin/add", methods=["POST"])
def add_tracking():
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("admin_dashboard"))

    tid = request.form["tracking_id"].upper()
    tracking_data[tid] = {
        "status": request.form["status"],
        "location": request.form["location"],
        "progress": int(request.form["progress"]),
        "progressStage": int(request.form["stage"]),
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "balance_due": 0,
        "history": [
            {"label": "Picked Up", "location": "Unknown", "done": True},
            {"label": "In Transit", "location": "Unknown", "done": False},
            {"label": "Mid-Route Checkpoint", "location": "Unknown", "done": False},
            {"label": "Border Clearance", "location": "Unknown", "done": False},
            {"label": "Out for Delivery", "location": "Unknown", "done": False},
            {"label": "Delivered", "location": "Unknown", "done": False}
        ]
    }
    save_data()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit/<tid>", methods=["GET", "POST"])
def edit_tracking(tid):
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        tracking_data[tid]["status"] = request.form["status"]
        tracking_data[tid]["location"] = request.form["location"]
        tracking_data[tid]["progress"] = int(request.form["progress"])
        tracking_data[tid]["progressStage"] = int(request.form["stage"])
        tracking_data[tid]["balance_due"] = float(request.form.get("balance_due", 0))
        tracking_data[tid]["updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_history = []
        i = 0
        while True:
            label_key = f"history_label_{i}"
            location_key = f"history_location_{i}"
            done_key = f"history_done_{i}"

            if label_key in request.form and location_key in request.form and done_key in request.form:
                new_history.append({
                    "label": request.form[label_key],
                    "location": request.form[location_key],
                    "done": request.form[done_key] == "True"
                })
                i += 1
            else:
                break

        tracking_data[tid]["history"] = new_history
        save_data()
        return redirect(url_for("admin_dashboard"))

    return render_template("edit_tracking.html", tid=tid, data=tracking_data.get(tid))

@app.route("/admin/delete/<tid>")
def delete_tracking(tid):
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("admin_dashboard"))

    tracking_data.pop(tid, None)
    save_data()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

# Static pages
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/price")
def price():
    return render_template("price.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/single")
def single():
    return render_template("single.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/quote")
def quote():
    return render_template("quote.html")

if __name__ == "__main__":
    app.run(debug=True)
