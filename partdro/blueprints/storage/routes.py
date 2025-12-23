from flask import request, jsonify
from flask_babel import _
from partdro.blueprints.storage import storage_bp
from partdro.services.storage import create_bucket, upload, get_public_url

@storage_bp.route("/storage/buckets", methods=["POST"])
def create_bucket_route():
    data = request.get_json(force=True, silent=True) or {}
    bucket_id = data.get("bucket_id") or "public-assets"
    public = bool(data.get("public", True))
    try:
        resp = create_bucket(bucket_id, public)
        return jsonify({"ok": True, "bucket": bucket_id, "public": public, "resp": getattr(resp, "data", None) or resp})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@storage_bp.route("/storage/upload", methods=["POST"])
def upload_route():
    bucket_id = request.form.get("bucket") or "public-assets"
    path = request.form.get("path")
    if not path or "file" not in request.files:
        return jsonify({"ok": False, "error": _("path and file are required")}), 400
    file = request.files["file"]
    content_type = file.content_type
    try:
        file_bytes = file.read()
        resp = upload(bucket_id, path, file_bytes, content_type=content_type, upsert=True)
        public_url = get_public_url(bucket_id, path)
        return jsonify({"ok": True, "path": path, "public_url": public_url})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@storage_bp.route("/storage/upload_text", methods=["POST"])
def upload_text_route():
    data = request.get_json(force=True, silent=True) or {}
    bucket_id = data.get("bucket") or "public-assets"
    path = data.get("path")
    text = data.get("text")
    if not path or text is None:
        return jsonify({"ok": False, "error": _("path and text are required")}), 400
    try:
        resp = upload(bucket_id, path, text.encode("utf-8"), content_type="text/plain", upsert=True)
        public_url = get_public_url(bucket_id, path)
        return jsonify({"ok": True, "path": path, "public_url": public_url})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@storage_bp.route("/storage/public_url", methods=["GET"])
def public_url_route():
    bucket_id = request.args.get("bucket") or "public-assets"
    path = request.args.get("path")
    if not path:
        return jsonify({"ok": False, "error": _("path is required")}), 400
    try:
        public_url = get_public_url(bucket_id, path)
        return jsonify({"ok": True, "public_url": public_url})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500
