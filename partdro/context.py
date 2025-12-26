from flask_babel import get_locale

def register_context(app):
    @app.context_processor
    def inject_vars():
        return {
            "site_name": "PartDro",
            "get_locale": get_locale
        }

