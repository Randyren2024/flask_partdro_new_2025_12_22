from flask import jsonify, render_template, request, abort, redirect, url_for
from flask_babel import _
from partdro.blueprints.main import main_bp
from partdro.services.db import instruments_count, list_products, get_product
from partdro.services.schema import fetch_openapi_schema, list_tables_from_openapi
from typing import Dict
import partdro.extensions as extensions

@main_bp.route("/health/db")
def db_health():
    try:
        count = instruments_count()
        return jsonify({"ok": True, "count": count})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@main_bp.route("/health/schema")
def schema_health():
    try:
        openapi = fetch_openapi_schema()
        tables = list_tables_from_openapi(openapi)
        return jsonify({"ok": True, "tables": tables})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# 首页与产品页路由

@main_bp.route("/")
def index():
    locale = request.args.get("locale", "en")
    # 可按分类读取示例数据用于首页分区展示
    infrared = list_products(category="Infrared Drones", page=1, page_size=6)
    cargo = list_products(category="Cargo Drones", page=1, page_size=6)
    spray = list_products(category="Spray Drones", page=1, page_size=6)
    products = infrared + cargo + spray
    return render_template("index.html", products=products, locale=locale)

@main_bp.route("/products")
def products_page():
    locale = request.args.get("locale", "en")
    category = request.args.get("category")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    products = list_products(category=category, page=page, page_size=page_size)
    return render_template("index.html", products=products, locale=locale)

_LP_TEMPLATE_MAP: Dict[str, str] = {
    "s150": "s150_landing_page.html",
    "s150_landing_page": "s150_landing_page.html",
    "s150_landing_page.html": "s150_landing_page.html",
    "s200": "test_s200_by_gemini.html",
    "test_s200_by_gemini": "test_s200_by_gemini.html",
    "gdu_s200_by_gemini.html": "test_s200_by_gemini.html",
}

@main_bp.route("/product/<int:product_id>")
def product_detail(product_id: int):
    locale = request.args.get("locale", "en")
    product = get_product(product_id)
    if not product:
        abort(404)
    lp = product.landing_page or ""
    template_name = _LP_TEMPLATE_MAP.get(lp)
    if not template_name:
        # 未配置映射时，降级返回首页或 404
        # 这里返回首页以便后续前端完善通用详情模板
        return render_template("index.html", products=[product], locale=locale)
    return render_template(template_name, product=product, locale=locale)

# 基础静态页（占位）

@main_bp.route("/about")
def about():
    return jsonify({"page": _("about")})

@main_bp.route("/terms-and-services")
def terms_and_services():
    return jsonify({"page": _("terms_and_services")})

@main_bp.route("/privacy-policy")
def privacy_policy():
    return jsonify({"page": _("privacy_policy")})

# 产品健康检查：验证 products 表与 landing_page 字段可读

@main_bp.route("/health/products")
def products_health():
    try:
        resp = extensions.supabase.table("products").select("landing_page").limit(1).execute()
        ok = resp is not None and hasattr(resp, "data")
        has_lp = False
        if ok and resp.data:
            row = resp.data[0]
            has_lp = "landing_page" in row
        return jsonify({"ok": bool(ok and has_lp), "has_landing_page": has_lp, "count": len(resp.data) if ok and resp.data else 0})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@main_bp.route("/i18n/set/<lang>")
def set_lang(lang: str):
    ref = request.headers.get("Referer") or url_for("index")
    resp = redirect(ref)
    resp.set_cookie("lang", lang, max_age=60*60*24*365)
    return resp
