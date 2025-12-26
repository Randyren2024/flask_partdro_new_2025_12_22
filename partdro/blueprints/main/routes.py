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
    
    # 获取四大分类数据 (每类取前6个)
    featured_products = {
        "infrared": list_products(category="Infrared Drones", page=1, page_size=6),
        "cargo": list_products(category="Cargo Drones", page=1, page_size=6),
        "spray": list_products(category="Spray Drones", page=1, page_size=6),
        "payloads": list_products(category="Payloads & Accessories", page=1, page_size=6)
    }
    
    return render_template("index.html", featured_products=featured_products, locale=locale)

@main_bp.route("/products")
def products_page():
    locale = request.args.get("locale", "en")
    category = request.args.get("category")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))
    products = list_products(category=category, page=page, page_size=page_size)
    return render_template("index.html", products=products, locale=locale) # 注意：这里复用 index.html，但 logic 可能需要调整，或者创建独立的 products.html。目前保持原样，只关注首页重构。

_LP_TEMPLATE_MAP: Dict[str, str] = {
    "s150": "s150_landing_page.html",
    "s150_landing_page": "s150_landing_page.html",
    "s150_landing_page.html": "s150_landing_page.html",
    "s200": "test_s200_by_gemini.html",
    "test_s200_by_gemini": "test_s200_by_gemini.html",
    "gdu_s200_by_gemini.html": "test_s200_by_gemini.html",
}

@main_bp.route("/api/apply-partner", methods=["POST"])
def apply_partner():
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    try:
        # 准备要写入的数据
        record = {
            "name": data.get("name"),
            "email": data.get("email"),
            "company": data.get("company"),
            "phone": data.get("phone"),
            "country": data.get("country"),
            "industries": data.get("industries", []),  # 数组
            "message": data.get("message")
        }
        
        # 写入 Supabase
        extensions.supabase.table("partner_applications").insert(record).execute()
        
        return jsonify({"success": True, "message": "Application submitted successfully"})
    except Exception as e:
        print(f"Error submitting application: {e}")
        return jsonify({"error": str(e)}), 500

@main_bp.route("/product/<product_id>")
def product_detail(product_id):
    locale = request.args.get("locale", "en")
    product = get_product(product_id)
    if not product:
        abort(404)
    lp = product.landing_page or ""
    
    # 1. 检查硬编码映射
    template_name = _LP_TEMPLATE_MAP.get(lp)
    
    # 2. 如果不在映射中，且看起来像是一个模板路径（以 .html 结尾），则尝试直接渲染
    if not template_name and lp.endswith(".html"):
        template_name = lp
        
    if not template_name:
        # 未配置映射且不是直接路径时，降级返回首页
        return render_template("index.html", products=[product], locale=locale)
        
    try:
        return render_template(template_name, product=product, locale=locale)
    except Exception as e:
        # 如果模板文件不存在或其他渲染错误，降级
        print(f"Template Error for {template_name}: {e}")
        return render_template("index.html", products=[product], locale=locale)

# 基础静态页（占位）

@main_bp.route("/about")
def about():
    return render_template("about.html")

@main_bp.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_and_conditions.html")

@main_bp.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")

@main_bp.route("/contact")
def contact():
    return render_template("contact.html")

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