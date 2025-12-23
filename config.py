import os
from pathlib import Path
from dotenv import load_dotenv

if os.getenv("FLASK_SKIP_DOTENV") != "1":
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=str(env_path))

class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY") or (
        "dev-secret-key" if ENV != "production" else None
    )
    if ENV == "production" and not SECRET_KEY:
        raise RuntimeError("FLASK_SECRET_KEY is required in production")

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL is required")

    SUPABASE_KEY = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY")
    )
    if not SUPABASE_KEY:
        raise RuntimeError("Supabase key is required")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    
    # Security Key for Debug/Admin Routes
    ADMIN_ACCESS_KEY = os.getenv("ADMIN_ACCESS_KEY")
