from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# In-memory DB
tracking_data = {
    "ABC123": {
        "status": "In Transit",
        "location": "Enugu",
        "progress": 50,
        "progressStage": 3,
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "history": [
            {"stage": 1, "label": "Order Placed", "icon": "fa-receipt"},
            {"stage": 2, "label": "Processing", "icon": "fa-cogs"},
            {"stage": 3, "label": "Shipped", "icon": "fa-shipping-fast"},
            {"stage": 4, "label": "Out for Delivery", "icon": "fa-truck"},
            {"stage": 5, "label": "Delivered", "icon": "fa-check-circle"}
        ]
    }
}

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
        return jsonify({"found": True, **data})
    else:
        return jsonify({"found": False, "message": f"Tracking ID '{tracking_id}' not found."})

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
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/edit/<tid>", methods=["GET", "POST"])
def edit_tracking(tid):
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        tracking_data[tid] = {
            "status": request.form["status"],
            "location": request.form["location"],
            "progress": int(request.form["progress"]),
            "progressStage": int(request.form["stage"]),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return redirect(url_for("admin_dashboard"))
    return render_template("edit_tracking.html", tid=tid, data=tracking_data.get(tid))

@app.route("/admin/delete/<tid>")
def delete_tracking(tid):
    if session.get("role") != "admin":
        flash("Access denied.")
        return redirect(url_for("admin_dashboard"))

    tracking_data.pop(tid, None)
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
