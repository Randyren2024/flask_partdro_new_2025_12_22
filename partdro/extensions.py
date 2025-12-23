from supabase import create_client, Client
from config import Config
from flask_babel import Babel
from flask import request

supabase: Client | None = None
babel: Babel | None = None

def init_supabase(app):
    global supabase
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def _normalize_lang(lang: str | None) -> str:
    val = (lang or "").lower()
    if not val:
        return "en"
    if val in ("zh", "zh-cn", "zh_cn", "cn"):
        return "zh_CN"
    if val in ("en", "en-us", "en_us", "us", "en-gb", "en_gb"):
        return "en"
    return val

def init_babel(app):
    global babel
    app.config.setdefault("BABEL_DEFAULT_LOCALE", "en")
    app.config.setdefault("BABEL_TRANSLATION_DIRECTORIES", "translations")
    def locale_selector():
        q = request.args.get("locale")
        c = request.cookies.get("lang")
        best = request.accept_languages.best_match(["en", "zh_CN"])
        return _normalize_lang(q or c or best or "en")
    babel = Babel(app, locale_selector=locale_selector)
