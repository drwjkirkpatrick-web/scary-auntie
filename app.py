"""
scary-auntie: Alaskan Native Ecological Knowledge Database
Main Flask application — "Hub of the Wheel" architecture.

  The botanical database is the HUB — the central reference.
  Knowledge Categories are the SPOKES — extensible topics that connect
  back to plants and to each other.
  Groups (clans, tribes, villages, schools) customize the wheel.

Two interfaces:
  1. Public site (children, youth, elders) — browse, contribute, explore
  2. Teacher/Admin backend — review, manage, customize

Author: scary-auntie project
"""

import os
import json
import secrets
from datetime import datetime, timezone
from functools import wraps
from flask import (Flask, render_template, request, redirect, url_for,
                   flash, jsonify, session, abort)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database import (
    init_database, get_connection,
    add_knowledge_entry, add_knowledge_record, add_block, verify_chain,
    get_all_plants, get_plant_by_id, get_plant_count, get_plant_categories,
    get_all_entries, review_entry, review_record,
    get_all_records, get_record_by_id, get_records_by_category,
    get_record_count, get_approved_records_with_coords,
    get_all_categories, get_category_by_slug, get_category_by_id,
    get_category_counts, add_category,
    get_all_groups, get_group_by_id, add_group, update_group,
    activate_group_category, get_group_categories,
    get_stats, get_blockchain_summary,
    get_user_by_username, create_user, get_all_users,
    seed_default_categories, seed_default_group,
)
import seed_data

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ── Upload settings ──
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# ── Items per page for paginated views ──
PER_PAGE = 24


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION DECORATORS
# ═══════════════════════════════════════════════════════════════

def login_required(f):
    """Decorator: redirect to login page if user is not authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access the admin area.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(min_role: str):
    """
    Decorator factory: require a minimum role level.
    Role hierarchy: student < teacher < admin.
    """
    role_order = {"student": 0, "teacher": 1, "admin": 2}

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in to access the admin area.", "error")
                return redirect(url_for("admin_login"))
            current = session.get("role", "student")
            if role_order.get(current, 0) < role_order.get(min_role, 0):
                flash("You do not have permission to access this area.", "error")
                return redirect(url_for("admin_dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ═══════════════════════════════════════════════════════════════
# PUBLIC SITE (Children / Youth / Elders)
# ═══════════════════════════════════════════════════════════════

@app.route("/")
def index():
    """Landing page — the hub of the wheel."""
    stats = get_stats()
    categories = get_all_categories()
    category_counts = get_category_counts()
    groups = get_all_groups()
    return render_template("index.html", stats=stats, categories=categories,
                           category_counts=category_counts, groups=groups)


@app.route("/plants")
def plant_list():
    """Browse all verified plants with pagination + search."""
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", PER_PAGE, type=int)
    per_page = min(per_page, 100)  # cap to prevent abuse
    offset = (page - 1) * per_page

    plants = get_all_plants(search=search, verified_only=True,
                            limit=per_page, offset=offset)
    total = get_plant_count() if not search else len(get_all_plants(search=search, verified_only=True))
    families = get_plant_categories()

    # Simple pagination calculation
    pages = max(1, (total + per_page - 1) // per_page)

    return render_template("plants.html", plants=plants, search=search,
                           page=page, pages=pages, per_page=per_page,
                           total=total, families=families)


@app.route("/plants/<int:plant_id>")
def plant_detail(plant_id):
    """View a single plant's details."""
    plant = get_plant_by_id(plant_id)
    if not plant:
        flash("Plant not found.", "error")
        return redirect(url_for("plant_list"))
    return render_template("plant_detail.html", plant=plant)


@app.route("/add-observation", methods=["GET", "POST"])
def add_observation():
    """
    Children, youth, and elders submit ecological observations here.
    This is the unified entry point for all knowledge categories.
    If a category is specified, the form adapts. Default: botanical.
    """
    if request.method == "POST":
        recorder_name = request.form.get("recorder_name", "").strip()
        recorder_age = request.form.get("recorder_age", "").strip()
        location = request.form.get("location_description", "").strip()
        latitude = request.form.get("latitude", "").strip()
        longitude = request.form.get("longitude", "").strip()
        observation = request.form.get("observation", "").strip()
        native_name_used = request.form.get("native_name_used", "").strip()
        plant_id = request.form.get("plant_id", "").strip()
        category_slug = request.form.get("category", "botanicals").strip()
        title = request.form.get("title", "").strip()
        tags = request.form.get("tags", "").strip()

        # Validation
        if not recorder_name:
            flash("Please enter your name.", "error")
            return redirect(url_for("add_observation"))

        if not observation:
            flash("Please describe what you observed.", "error")
            return redirect(url_for("add_observation"))

        # Parse optional fields
        age = int(recorder_age) if recorder_age.isdigit() else None
        lat = float(latitude) if latitude else None
        lng = float(longitude) if longitude else None
        pid = int(plant_id) if plant_id and plant_id.isdigit() else None

        # Handle photo upload
        photo_path = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Prefix with timestamp to avoid collisions
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(save_path)
                photo_path = f"uploads/{filename}"

        # Route to the appropriate storage based on category
        category = get_category_by_slug(category_slug)
        if category:
            add_knowledge_record(
                category_id=category["id"],
                recorder_name=recorder_name,
                title=title or None,
                plant_id=pid,
                recorder_age=age,
                location_description=location or None,
                latitude=lat,
                longitude=lng,
                observation=observation,
                native_name_used=native_name_used or None,
                tags=tags or None,
                photo_path=photo_path
            )
        else:
            # Fallback to legacy botanical entry
            add_knowledge_entry(
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
    category_slug = request.args.get("category", "botanicals")
    category = get_category_by_slug(category_slug)
    plants = get_all_plants(verified_only=True) if category and category.get("is_hub") else []
    categories = get_all_categories()
    return render_template("add_observation.html", plants=plants,
                           categories=categories,
                           current_category=category,
                           preselect_plant_id=request.args.get("plant_id", ""))


# Keep the old route for backward compatibility
@app.route("/add-entry", methods=["GET", "POST"])
def add_entry():
    """Legacy route — redirects to the unified add-observation endpoint."""
    return redirect(url_for("add_observation", **request.args))


@app.route("/map")
def map_view():
    """Interactive map of all approved observations across all categories."""
    entries = get_approved_records_with_coords()
    # Also include legacy approved entries
    legacy = get_all_entries(status="approved")
    groups = get_all_groups()
    return render_template("map.html", entries=entries, legacy=legacy, groups=groups)


# ═══════════════════════════════════════════════════════════════
# KNOWLEDGE CATEGORIES (SPOKES OF THE WHEEL)
# ═══════════════════════════════════════════════════════════════

@app.route("/knowledge")
def knowledge_wheel():
    """The wheel view — all knowledge categories at a glance."""
    categories = get_all_categories()
    category_counts = get_category_counts()
    stats = get_stats()
    return render_template("knowledge_wheel.html", categories=categories,
                           category_counts=category_counts, stats=stats)


@app.route("/knowledge/<slug>")
def category_view(slug):
    """Browse observations within a knowledge category."""
    category = get_category_by_slug(slug)
    if not category:
        flash("Knowledge category not found.", "error")
        return redirect(url_for("knowledge_wheel"))

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", PER_PAGE, type=int)
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page

    records = get_records_by_category(category["id"], limit=per_page, offset=offset)
    total = len(get_records_by_category(category["id"]))

    # Also show legacy botanical entries if this is the hub
    legacy_entries = []
    if category.get("is_hub"):
        legacy_entries = get_all_entries(limit=50)

    pages = max(1, (total + per_page - 1) // per_page)

    return render_template("category_view.html", category=category,
                           records=records, legacy_entries=legacy_entries,
                           page=page, pages=pages, total=total)


@app.route("/knowledge/<slug>/<int:record_id>")
def record_detail(slug, record_id):
    """View a single knowledge record."""
    category = get_category_by_slug(slug)
    if not category:
        flash("Knowledge category not found.", "error")
        return redirect(url_for("knowledge_wheel"))

    record = get_record_by_id(record_id)
    if not record or record["category_id"] != category["id"]:
        flash("Record not found.", "error")
        return redirect(url_for("category_view", slug=slug))

    return render_template("record_detail.html", category=category, record=record)


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
        if user and check_password_hash(user["password_hash"], password):
            # Regenerate session ID to prevent session fixation
            session.clear()
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


@app.route("/admin")
@login_required
def admin_dashboard():
    """Admin dashboard with overview stats."""
    stats = get_stats()
    chain_summary = get_blockchain_summary()
    recent_entries = get_all_entries()[:10]
    pending_entries = get_all_entries(status="pending")[:10]
    recent_records = get_all_records()[:10]
    pending_records = get_all_records(status="pending")[:10]

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        chain=chain_summary,
        recent=recent_entries,
        pending=pending_entries,
        recent_records=recent_records,
        pending_records=pending_records,
        user=session
    )


@app.route("/admin/entries")
@login_required
def admin_entries():
    """View and filter all legacy botanical knowledge entries."""
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", PER_PAGE, type=int)
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page

    if status_filter in ("pending", "approved", "flagged"):
        entries = get_all_entries(status=status_filter, limit=per_page, offset=offset)
        total = len(get_all_entries(status=status_filter))
    else:
        entries = get_all_entries(limit=per_page, offset=offset)
        total = len(get_all_entries())

    pages = max(1, (total + per_page - 1) // per_page)

    return render_template("admin/entries.html", entries=entries,
                           status_filter=status_filter,
                           page=page, pages=pages, total=total,
                           user=session)


@app.route("/admin/entries/<int:entry_id>", methods=["GET", "POST"])
@login_required
def admin_entry_detail(entry_id):
    """Review a single legacy knowledge entry."""
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


@app.route("/admin/records")
@login_required
def admin_records():
    """View and filter all knowledge records (new system)."""
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", PER_PAGE, type=int)
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page

    if status_filter in ("pending", "approved", "flagged"):
        records = get_all_records(status=status_filter, limit=per_page, offset=offset)
        total = get_record_count(status=status_filter)
    else:
        records = get_all_records(limit=per_page, offset=offset)
        total = get_record_count()

    pages = max(1, (total + per_page - 1) // per_page)

    return render_template("admin/records.html", records=records,
                           status_filter=status_filter,
                           page=page, pages=pages, total=total,
                           user=session)


@app.route("/admin/records/<int:record_id>", methods=["GET", "POST"])
@login_required
def admin_record_detail(record_id):
    """Review a single knowledge record."""
    record = get_record_by_id(record_id)
    if not record:
        flash("Record not found.", "error")
        return redirect(url_for("admin_records"))

    if request.method == "POST":
        action = request.form.get("action")
        notes = request.form.get("review_notes", "").strip()
        reviewer = session.get("display_name", session.get("username", "Unknown"))

        if action == "approve":
            review_record(record_id, reviewer, 1, notes)
            flash("Record approved.", "success")
        elif action == "flag":
            review_record(record_id, reviewer, 2, notes)
            flash("Record flagged for review.", "warning")
        else:
            flash("Invalid action.", "error")

        return redirect(url_for("admin_records"))

    return render_template("admin/record_detail.html", record=record, user=session)


@app.route("/admin/plants")
@role_required("teacher")
def admin_plants():
    """Manage plants in the database."""
    search = request.args.get("search", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", PER_PAGE, type=int)
    per_page = min(per_page, 100)
    offset = (page - 1) * per_page

    plants = get_all_plants(search=search, limit=per_page, offset=offset)
    total = get_plant_count()
    pages = max(1, (total + per_page - 1) // per_page)

    return render_template("admin/plants.html", plants=plants, search=search,
                           page=page, pages=pages, total=total, user=session)


@app.route("/admin/plants/add", methods=["GET", "POST"])
@role_required("teacher")
def admin_add_plant():
    """Add a new verified plant to the database."""
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


@app.route("/admin/categories")
@role_required("teacher")
def admin_categories():
    """Manage knowledge categories."""
    categories = get_all_categories()
    category_counts = get_category_counts()
    return render_template("admin/categories.html", categories=categories,
                           category_counts=category_counts, user=session)


@app.route("/admin/categories/add", methods=["POST"])
@role_required("admin")
def admin_add_category():
    """Add a new knowledge category."""
    slug = request.form.get("slug", "").strip().lower()
    display_name = request.form.get("display_name", "").strip()
    icon = request.form.get("icon", "").strip() or None
    description = request.form.get("description", "").strip() or None

    if not slug or not display_name:
        flash("Slug and display name are required.", "error")
        return redirect(url_for("admin_categories"))

    # Sanitize slug — only lowercase letters, numbers, hyphens
    import re
    slug = re.sub(r'[^a-z0-9-]', '-', slug)

    try:
        add_category(slug=slug, display_name=display_name, icon=icon,
                     description=description, is_hub=False)
        flash(f"Category '{display_name}' created.", "success")
    except Exception as e:
        flash(f"Error creating category: {e}", "error")

    return redirect(url_for("admin_categories"))


@app.route("/admin/groups")
@role_required("admin")
def admin_groups():
    """Manage community groups."""
    groups = get_all_groups()
    categories = get_all_categories()
    return render_template("admin/groups.html", groups=groups,
                           categories=categories, user=session)


@app.route("/admin/groups/add", methods=["POST"])
@role_required("admin")
def admin_add_group():
    """Create a new community group."""
    name = request.form.get("name", "").strip()
    group_type = request.form.get("group_type", "").strip() or None
    description = request.form.get("description", "").strip() or None
    native_language = request.form.get("native_language", "").strip() or None
    region = request.form.get("region", "").strip() or None
    map_lat = request.form.get("map_center_lat", 64.5, type=float)
    map_lng = request.form.get("map_center_lng", -150.0, type=float)
    map_zoom = request.form.get("map_zoom", 4, type=int)
    primary_color = request.form.get("primary_color", "#2d5a3d").strip()
    accent_color = request.form.get("accent_color", "#c4a35a").strip()

    if not name:
        flash("Group name is required.", "error")
        return redirect(url_for("admin_groups"))

    group_id = add_group(
        name=name, group_type=group_type, description=description,
        native_language=native_language, region=region,
        map_center_lat=map_lat, map_center_lng=map_lng, map_zoom=map_zoom,
        primary_color=primary_color, accent_color=accent_color
    )

    # Activate all default categories for the new group
    categories = get_all_categories()
    for i, cat in enumerate(categories):
        activate_group_category(group_id, cat["id"], display_order=i)

    flash(f"Group '{name}' created with all categories activated.", "success")
    return redirect(url_for("admin_groups"))


@app.route("/admin/groups/<int:group_id>/activate/<int:category_id>", methods=["POST"])
@role_required("admin")
def admin_activate_category(group_id, category_id):
    """Activate a knowledge category for a group."""
    display_order = request.form.get("display_order", 0, type=int)
    activate_group_category(group_id, category_id, display_order)
    flash("Category activated for this group.", "success")
    return redirect(url_for("admin_groups"))


@app.route("/admin/blockchain")
@login_required
def admin_blockchain():
    """View blockchain integrity status."""
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
@role_required("admin")
def admin_users():
    """Manage teacher/admin users."""
    users = get_all_users()
    groups = get_all_groups()
    return render_template("admin/users.html", users=users, groups=groups, user=session)


@app.route("/admin/users/add", methods=["POST"])
@role_required("admin")
def admin_add_user():
    """Add a new teacher or admin user."""
    username = request.form.get("username", "").strip()
    display_name = request.form.get("display_name", "").strip()
    password = request.form.get("password", "").strip()
    role = request.form.get("role", "teacher").strip()
    group_id = request.form.get("group_id", "").strip()

    if not username or not display_name or not password:
        flash("All fields are required.", "error")
        return redirect(url_for("admin_users"))

    gid = int(group_id) if group_id.isdigit() else None

    try:
        create_user(username, display_name,
                    generate_password_hash(password), role, group_id=gid)
        flash(f"User '{display_name}' created successfully.", "success")
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for("admin_users"))


# ═══════════════════════════════════════════════════════════════
# API ENDPOINTS (for map and frontend interactivity)
# All API endpoints now require session authentication.
# ═══════════════════════════════════════════════════════════════

@app.route("/api/plants")
@login_required
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
@login_required
def api_approved_entries():
    """JSON API for approved entries with coordinates."""
    records = get_approved_records_with_coords()
    result = []
    for r in records:
        result.append({
            "id": r["id"],
            "recorder_name": r["recorder_name"],
            "title": r.get("title"),
            "location": r["location_description"],
            "lat": r["latitude"],
            "lng": r["longitude"],
            "observation": r["observation"],
            "category": r.get("category_name", "Unknown"),
            "plant_name": r.get("plant_name") or r.get("plant_english_name") or "Unknown plant",
            "date": r["entry_date"]
        })

    # Also include legacy entries
    legacy = get_all_entries(status="approved")
    for e in legacy:
        if e.get("latitude") and e.get("longitude"):
            result.append({
                "id": e["id"],
                "recorder_name": e["recorder_name"],
                "title": None,
                "location": e["location_description"],
                "lat": e["latitude"],
                "lng": e["longitude"],
                "observation": e["observation"],
                "category": "Botanical Knowledge",
                "plant_name": e.get("plant_english_name", "Unknown plant"),
                "date": e["entry_date"]
            })

    return jsonify(result)


@app.route("/api/categories")
def api_categories():
    """JSON API for knowledge categories (public — category list is not sensitive)."""
    categories = get_all_categories()
    counts = get_category_counts()
    return jsonify([{
        "id": c["id"],
        "slug": c["slug"],
        "display_name": c["display_name"],
        "icon": c["icon"],
        "is_hub": bool(c["is_hub"]),
        "record_count": counts.get(c["slug"], 0)
    } for c in categories])


@app.route("/api/verify")
@login_required
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
    from database import create_user
    from werkzeug.security import generate_password_hash

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()

    if count == 0:
        default_password = os.environ.get("ADMIN_PASSWORD", "scary-auntie-admin")
        create_user("admin", "Administrator",
                    generate_password_hash(default_password), "admin")
        print(f"Default admin created: username=admin")
        print("Set ADMIN_PASSWORD environment variable or change it in the admin panel.")
        print("CHANGE THIS PASSWORD IN PRODUCTION!")


if __name__ == "__main__":
    # Initialize database schema
    init_database()

    # Seed default knowledge categories
    seed_default_categories()

    # Seed default group
    seed_default_group()

    # Seed plant data only if empty
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

    # Run the Flask app — debug off by default for safety
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=9192, debug=debug)