from flask import Flask
from pathlib import Path
from config import Config
from partdro.extensions import init_supabase
from partdro.extensions import init_babel
from partdro.blueprints.main import main_bp
from partdro.blueprints.storage import storage_bp
from partdro.errors import register_error_handlers
from partdro.context import register_context
from partdro.logging import configure_logging
from partdro.cli import register_cli

def create_app():
    root = Path(__file__).resolve().parent.parent
    app = Flask(__name__, template_folder=str(root / "templates"), static_folder=str(root / "static"))
    app.config.from_object(Config)
    init_supabase(app)
    init_babel(app)
    configure_logging(app)
    register_context(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(storage_bp)
    
    # Register Debug Blueprint (Always registered, secured by Key in routes.py)
    from partdro.blueprints.debug import debug_bp
    app.register_blueprint(debug_bp)
        
    register_error_handlers(app)
    register_cli(app)
    return app
