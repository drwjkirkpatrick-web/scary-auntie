"""
scary-auntie: Alaskan Native Ecological Knowledge Database
Main Flask application with two interfaces:
  1. Public entry site (children/adolescents)
  2. Teacher/Admin backend

Author: scary-auntie project
"""

import os
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename

# Import our database module
from database import (
    init_database, get_connection,
    add_knowledge_entry, add_block, verify_chain,
    get_all_plants, get_plant_by_id, get_all_entries, review_entry,
    get_stats, get_blockchain_summary, get_user_by_username, create_user
)
import seed_data

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "scary-auntie-dev-key-change-in-production")

# Upload settings
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def hash_password(password: str) -> str:
    """Simple password hashing. In production, use werkzeug.security.generate_password_hash."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════
# PUBLIC SITE (Children / Adolescents)
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Landing page for the public site."""
    stats = get_stats()
    return render_template("index.html", stats=stats)


@app.route("/plants")
def plant_list():
    """Browse all verified plants."""
    search = request.args.get("search", "").strip()
    plants = get_all_plants(search=search, verified_only=True)
    return render_template("plants.html", plants=plants, search=search)


@app.route("/plants/<int:plant_id>")
def plant_detail(plant_id):
    """View a single plant's details."""
    plant = get_plant_by_id(plant_id)
    if not plant:
        flash("Plant not found.", "error")
        return redirect(url_for("plant_list"))
    return render_template("plant_detail.html", plant=plant)


@app.route("/add-entry", methods=["GET", "POST"])
def add_entry():
    """Children and adolescents submit ecological observations here."""
    if request.method == "POST":
        recorder_name = request.form.get("recorder_name", "").strip()
        recorder_age = request.form.get("recorder_age", "").strip()
        location = request.form.get("location_description", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        observation = request.form.get("observation", "").strip()
        native_name_used = request.form.get("native_name_used", "").strip()
        plant_id = request.form.get("plant_id", "").strip()

        # Validation
        if not recorder_name:
            flash("Please enter your name.", "error")
            return redirect(url_for("add_entry"))

        if not observation:
            flash("Please describe what you observed.", "error")
            return redirect(url_for("add_entry"))

        # Parse optional fields
        age = int(recorder_age) if recorder_age.isdigit() else None
        lat = float(latitude) if latitude else None
        lng = float(longitude) if longitude else None
        pid = int(plant_id) if plant_id.isdigit() else None

        # Handle photo upload
        photo_path = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Prefix with timestamp to avoid collisions
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)
                photo_path = f"uploads/{filename}"

        entry_id = add_knowledge_entry(
            plant_id=pid,
            recorder_name=recorder_name,
            recorder_age=age,
            location_description=location,
            latitude=lat,
            longitude=lng,
            observation=observation,
            native_name_used=native_name_used,
            photo_path=photo_path
        )

        flash("Thank you! Your observation has been recorded and will be reviewed by a teacher.", "success")
        return redirect(url_for("index"))

    # GET: show the form
    plants = get_all_plants(verified_only=True)
    return render_template("add_entry.html", plants=plants)


@app.route("/map")
def map_view():
    """Interactive map of all approved observations."""
    entries = get_all_entries(status="approved")
    return render_template("map.html", entries=entries)


# ═══════════════════════════════════════════════════════════════
# TEACHER / ADMIN BACKEND
# ═══════════════════════════════════════════════════════════════

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Login page for teachers and administrators."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        user = get_user_by_username(username)
        if user and user["password_hash"] == hash_password(password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["display_name"] = user["display_name"]
            flash(f"Welcome, {user['display_name']}!")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    """Log out of admin session."""
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("admin_login"))


def require_admin():
    """Check if user is logged in. Returns user dict or redirects."""
    if "user_id" not in session:
        flash("Please log in to access the admin area.", "error")
        return redirect(url_for("admin_login"))
    return None


def require_role(min_role: str):
    """Check if user has required role (admin > teacher > student)."""
    role_order = {"student": 0, "teacher": 1, "admin": 2}
    current = session.get("role", "student")
    if role_order.get(current, 0) < role_order.get(min_role, 0):
        flash("You do not have permission to access this area.", "error")
        return redirect(url_for("admin_dashboard"))
    return None


@app.route("/admin")
def admin_dashboard():
    """Admin dashboard with overview stats."""
    redir = require_admin()
    if redir:
        return redir

    stats = get_stats()
    chain_summary = get_blockchain_summary()
    recent_entries = get_all_entries()[:10]
    pending_entries = get_all_entries(status="pending")[:10]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        chain=chain_summary,
        recent=recent_entries,
        pending=pending_entries,
        user=session
    )


@app.route("/admin/entries")
def admin_entries():
    """View and filter all knowledge entries."""
    redir = require_admin()
    if redir:
        return redir

    status_filter = request.args.get("status", "")
    if status_filter in ("pending", "approved", "flagged"):
        entries = get_all_entries(status=status_filter)
    else:
        entries = get_all_entries()

    return render_template("admin/entries.html", entries=entries,
                           status_filter=status_filter, user=session)


@app.route("/admin/entries/<int:entry_id>", methods=["GET", "POST"])
def admin_entry_detail(entry_id):
    """Review a single knowledge entry."""
    redir = require_admin()
    if redir:
        return redir

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ke.*, p.english_name as plant_english_name,
               p.latin_binomial, p.native_alaskan_name as plant_native_name
        FROM knowledge_entries ke
        LEFT JOIN plants p ON ke.plant_id = p.id
        WHERE ke.id = ?
    """, (entry_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        flash("Entry not found.", "error")
        return redirect(url_for("admin_entries"))

    entry = dict(row)

    if request.method == "POST":
        action = request.form.get("action")
        notes = request.form.get("review_notes", "").strip()
        reviewer = session.get("display_name", session.get("username", "Unknown"))

        if action == "approve":
            review_entry(entry_id, reviewer, 1, notes)
            flash("Entry approved.", "success")
        elif action == "flag":
            review_entry(entry_id, reviewer, 2, notes)
            flash("Entry flagged for review.", "warning")
        else:
            flash("Invalid action.", "error")

        return redirect(url_for("admin_entries"))

    return render_template("admin/entry_detail.html", entry=entry, user=session)


@app.route("/admin/plants")
def admin_plants():
    """Manage plants in the database."""
    redir = require_admin()
    if redir:
        return redir

    redir = require_role("teacher")
    if redir:
        return redir

    plants = get_all_plants()
    return render_template("admin/plants.html", plants=plants, user=session)


@app.route("/admin/plants/add", methods=["GET", "POST"])
def admin_add_plant():
    """Add a new verified plant to the database."""
    redir = require_admin()
    if redir:
        return redir

    redir = require_role("teacher")
    if redir:
        return redir

    if request.method == "POST":
        from database import add_plant

        latin = request.form.get("latin_binomial", "").strip()
        english = request.form.get("english_name", "").strip()
        native_name = request.form.get("native_alaskan_name", "").strip() or None
        native_lang = request.form.get("native_language", "").strip() or None
        family = request.form.get("family", "").strip() or None
        description = request.form.get("description", "").strip() or None
        habitat = request.form.get("habitat", "").strip() or None
        uses = request.form.get("traditional_uses", "").strip() or None
        parts = request.form.get("parts_used", "").strip() or None
        prep = request.form.get("preparation", "").strip() or None
        cautions = request.form.get("cautions", "").strip() or None
        source_author = request.form.get("source_author", "").strip() or None
        source_url = request.form.get("source_url", "").strip() or None

        if not latin or not english:
            flash("Latin binomial and English name are required.", "error")
            return redirect(url_for("admin_add_plant"))

        plant_id = add_plant(
            latin_binomial=latin,
            english_name=english,
            native_alaskan_name=native_name,
            native_language=native_lang,
            family=family,
            description=description,
            habitat=habitat,
            traditional_uses=uses,
            parts_used=parts,
            preparation=prep,
            cautions=cautions,
            verified=True,
            source_author=source_author,
            source_url=source_url
        )

        flash(f"Plant '{english}' added successfully.", "success")
        return redirect(url_for("admin_plants"))

    return render_template("admin/add_plant.html", user=session)


@app.route("/admin/blockchain")
def admin_blockchain():
    """View blockchain integrity status."""
    redir = require_admin()
    if redir:
        return redir

    chain_summary = get_blockchain_summary()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, table_name, record_id, operation, timestamp,
               recorder_name, block_hash
        FROM block_chain ORDER BY id DESC LIMIT 50
    """)
    recent_blocks = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template("admin/blockchain.html",
                           chain=chain_summary,
                           blocks=recent_blocks,
                           user=session)


@app.route("/admin/users")
def admin_users():
    """Manage teacher/admin users."""
    redir = require_admin()
    if redir:
        return redir

    redir = require_role("admin")
    if redir:
        return redir

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, display_name, role, active, created_at FROM users ORDER BY id DESC")
    users = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return render_template("admin/users.html", users=users, user=session)


@app.route("/admin/users/add", methods=["POST"])
def admin_add_user():
    """Add a new teacher or admin user."""
    redir = require_admin()
    if redir:
        return redir

    redir = require_role("admin")
    if redir:
        return redir

    username = request.form.get("username", "").strip()
    display_name = request.form.get("display_name", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "teacher").strip()

    if not username or not display_name or not password:
        flash("All fields are required.", "error")
        return redirect(url_for("admin_users"))

    try:
        create_user(username, display_name, hash_password(password), role)
        flash(f"User '{display_name}' created successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("admin_users"))


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS (for map and frontend interactivity)
# ═══════════════════════════════════════════════════════════════

@app.route("/api/plants")
def api_plants():
    """JSON API for plant list (used by entry form and map)."""
    search = request.args.get("search", "").strip()
    plants = get_all_plants(search=search, verified_only=True)
    return jsonify([{
        "id": p["id"],
        "latin_binomial": p["latin_binomial"],
        "english_name": p["english_name"],
        "native_alaskan_name": p["native_alaskan_name"],
        "family": p["family"]
    } for p in plants])


@app.route("/api/entries/approved")
def api_approved_entries():
    """JSON API for approved entries with coordinates."""
    entries = get_all_entries(status="approved")
    result = []
    for e in entries:
        if e.get("latitude") and e.get("longitude"):
            result.append({
                "id": e["id"],
                "recorder_name": e["recorder_name"],
                "location": e["location_description"],
                "lat": e["latitude"],
                "lng": e["longitude"],
                "observation": e["observation"],
                "plant_name": e.get("plant_english_name", "Unknown plant"),
                "date": e["entry_date"]
            })
    return jsonify(result)


@app.route("/api/verify")
def api_verify():
    """Verify blockchain integrity via API."""
    tampered = verify_chain()
    return jsonify({
        "integrity_ok": len(tampered) == 0,
        "tampered_count": len(tampered),
        "tampered_blocks": tampered
    })


# ═══════════════════════════════════════════════════════════════
# INITIALIZATION
# ═══════════════════════════════════════════════════════════════

def setup_default_admin():
    """Create a default admin user if none exists."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        create_user("admin", "Administrator",
                    hash_password("scary-auntie-admin"), "admin")
        print("Default admin created: username=admin, password=scary-auntie-admin")
        print("CHANGE THIS PASSWORD IN PRODUCTION!")


if __name__ == "__main__":
    # Initialize database and seed data (only if empty)
    init_database()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM plants")
    existing = cursor.fetchone()[0]
    conn.close()
    if existing == 0:
        seeded = seed_data.seed_verified_plants()
        print(f"Database initialized. Seeded {seeded} verified plants.")
    else:
        print(f"Database already has {existing} plants. Skipping seed.")

    # Create default admin
    setup_default_admin()

    # Run the Flask app
    app.run(host="0.0.0.0", port=9192, debug=True)
