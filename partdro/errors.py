from flask import jsonify
from flask_babel import _

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": _("not found")}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": _("server error")}), 500
