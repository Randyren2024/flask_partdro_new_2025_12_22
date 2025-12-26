from flask import Blueprint, render_template, request, jsonify, current_app, abort
from partdro.services.ai import translate_product_info
from partdro.services.storage import upload, get_public_url
from partdro.services.lp_generator import generate_lp_html
import partdro.extensions as extensions
import traceback

import os

# Point to the root 'templates' directory
# routes.py is in partdro/blueprints/debug/
# templates is in templates/ (root)
# So we need to go up 3 levels: ../../../templates
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'templates'))

debug_bp = Blueprint("debug", __name__, url_prefix="/debug", template_folder=template_dir)

@debug_bp.before_request
def restrict_access():
    # Allow if in development environment
    if current_app.config.get("ENV") != "production":
        return

    # In production, require ADMIN_ACCESS_KEY
    admin_key = current_app.config.get("ADMIN_ACCESS_KEY")
    if not admin_key:
        # If no key configured, disable debug entirely in prod
        abort(403, "Debug tools disabled: ADMIN_ACCESS_KEY not configured.")
        
    # Check query param or header
    request_key = request.args.get("key") or request.headers.get("X-Admin-Key")
    
    if request_key != admin_key:
        abort(403, "Access Denied: Invalid Admin Key.")

@debug_bp.route("/")
def index():
    # Check supabase connection
    supabase_status = "Unknown"
    categories = []
    
    try:
        # Check connection
        extensions.supabase.table("product").select("id").limit(1).execute()
        supabase_status = "Connected"
        
        # Fetch categories for dropdown
        # Assuming there is a 'category' table or we just fetch distinct from products if not
        # Let's try to fetch from 'category' table first, if it exists.
        # Based on previous context, user mentioned 'category_id' in product table.
        # Let's assume a 'category' table exists with id, name.
        # If not, we might need to fallback or just use hardcoded common ones.
        
        # Safe try to fetch categories
        try:
            res = extensions.supabase.table("category").select("id, name").execute()
            categories = res.data if res.data else []
        except:
            # Fallback if category table missing or other issue
            categories = []
            
    except Exception as e:
        supabase_status = f"Error: {str(e)}"
        
    return render_template("debug.html", supabase_status=supabase_status, categories=categories)

@debug_bp.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True) or {}
    name = data.get("name")
    desc = data.get("description")
    
    if not name:
        return jsonify({"ok": False, "error": "Name is required"}), 400
        
    try:
        result = translate_product_info(name, desc or "")
        return jsonify({"ok": True, "data": result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@debug_bp.route("/upload_product", methods=["POST"])
def upload_product():
    # 1. Handle image upload if present
    file = request.files.get("image_file")
    image_url = request.form.get("image_url")
    
    if file:
        try:
            file_bytes = file.read()
            # Simple filename based on product_id_no or random
            pid = request.form.get("product_id_no", "temp")
            filename = f"{pid}_{file.filename}"
            bucket = "product-thumbnails"
            upload(bucket, filename, file_bytes, content_type=file.content_type, upsert=True)
            image_url = get_public_url(bucket, filename)
        except Exception as e:
            return jsonify({"ok": False, "error": f"Image upload failed: {str(e)}"}), 500

    # 2. Prepare database record
    try:
        record = {
            "product_id_no": request.form.get("product_id_no"),
            "category_id": request.form.get("category_id") or None,
            "landing_page": request.form.get("landing_page"),
            "model": request.form.get("model"),
            "name": request.form.get("name"),
            "description": request.form.get("description"),
            "thumbnail": image_url,
            # Translations
            "name_en": request.form.get("name_en"),
            "name_ja": request.form.get("name_ja"),
            "name_es": request.form.get("name_es"),
            "description_en": request.form.get("description_en"),
            "description_ja": request.form.get("description_ja"),
            "description_es": request.form.get("description_es"),
        }
        
        # Upsert into Supabase
        extensions.supabase.table("product").upsert(record, on_conflict="product_id_no").execute()
        
        return jsonify({"ok": True, "message": "Product uploaded successfully", "image_url": image_url})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": str(e)}), 500

import csv
import io

@debug_bp.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("csv_file")
    if not file:
        return jsonify({"ok": False, "error": "No CSV file provided"}), 400

    try:
        # Read and parse CSV
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline=None)
        reader = csv.DictReader(stream)
        
        rows = []
        for row in reader:
            # Basic validation
            if not row.get("product_id_no") or not row.get("model") or not row.get("name"):
                continue
                
            # Clean empty strings to None
            cleaned_row = {k: (v.strip() if v and v.strip() else None) for k, v in row.items()}
            
            # Ensure category_id is int or None
            if cleaned_row.get("category_id"):
                try:
                    cleaned_row["category_id"] = int(cleaned_row["category_id"])
                except:
                    cleaned_row["category_id"] = None
            
            rows.append(cleaned_row)
            
        if not rows:
            return jsonify({"ok": False, "error": "No valid rows found in CSV"}), 400

        # Bulk Upsert
        extensions.supabase.table("product").upsert(rows, on_conflict="product_id_no").execute()
        
        return jsonify({"ok": True, "message": f"Successfully processed {len(rows)} products"})
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"ok": False, "error": f"CSV processing failed: {str(e)}"}), 500

@debug_bp.route("/generate-lp", methods=["POST"])
def generate_lp():
    data = request.get_json(force=True) or {}
    product_id = data.get("productId")
    hero_media = data.get("heroMedia")
    features = data.get("features", [])
    
    if not product_id:
        return jsonify({"ok": False, "error": "Product ID is required"}), 400
        
    try:
        # Try to get the product name from Supabase for a better title
        res = extensions.supabase.table("product").select("name").eq("product_id_no", product_id).execute()
        product_name = res.data[0].get("name") if res.data else product_id
        
        html = generate_lp_html(product_name, hero_media, features)
        return jsonify({"ok": True, "html": html})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@debug_bp.route("/save-lp", methods=["POST"])
def save_lp():
    data = request.get_json(force=True) or {}
    product_id = data.get("productId")
    html = data.get("html")
    
    if not product_id or not html:
        return jsonify({"ok": False, "error": "Missing product_id or html"}), 400
        
    try:
        # 1. Save HTML to file
        filename = f"generated_{product_id}.html"
        # Ensure 'templates/generated' directory exists
        gen_dir = os.path.join(template_dir, "generated")
        if not os.path.exists(gen_dir):
            os.makedirs(gen_dir)
            
        file_path = os.path.join(gen_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        # 2. Update Supabase
        # We set landing_page to the relative path within templates
        extensions.supabase.table("product").update({"landing_page": f"generated/{filename}"}).eq("product_id_no", product_id).execute()
        
        return jsonify({"ok": True, "message": f"Saved to {filename} and updated database"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
