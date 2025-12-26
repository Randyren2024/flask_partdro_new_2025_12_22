import partdro.extensions as extensions
from typing import Any, Dict, List, Optional

def instruments_count():
    resp = extensions.supabase.table("instruments").select("id").limit(1).execute()
    return len(resp.data) if getattr(resp, "data", None) else 0

class ProductVM:
    def __init__(self, data: Dict[str, Any]):
        self._data = data or {}

    @property
    def id(self) -> Optional[int]:
        return self._data.get("id")

    @property
    def product_id_no(self) -> Optional[str]:
        return self._data.get("product_id_no")

    @property
    def category_id(self) -> Optional[int]:
        return self._data.get("category_id")

    @property
    def category(self) -> Optional[str]:
        # 暂时硬编码映射，或者后续通过 join 查询实现
        cat_id = self.category_id
        mapping = {
            1: "Infrared Drones", 
            2: "Cargo Drones", 
            3: "Spray Drones",
            4: "Payloads & Accessories"
        }
        return mapping.get(cat_id)

    @property
    def image_url(self) -> Optional[str]:
        return self._data.get("thumbnail") or self._data.get("image_url")

    @property
    def landing_page(self) -> Optional[str]:
        lp = self._data.get("landing_page")
        if isinstance(lp, str):
            return lp.strip().lower()
        return None

    def get_translated_name(self, locale: str = "en") -> str:
        # 处理 Flask-Babel 返回的 Locale 对象
        if hasattr(locale, 'language'):
            locale = str(locale)
        locale = (locale or "en").lower()
        # 映射 Babel locale 到数据库字段
        # zh_cn -> name (默认是中文), name_zh, name_cn
        # en -> name_en, name
        # ja -> name_ja, name
        # es -> name_es, name
        name_keys = []
        if locale == "zh_cn":
            name_keys = ["name", "name_zh", "name_cn", "title"]
        elif locale == "ja":
            name_keys = ["name_ja", "name", "title"]
        elif locale == "es":
            name_keys = ["name_es", "name", "title"]
        else:
            name_keys = [f"name_{locale}", "name", "title"]
            
        for key in name_keys:
            val = self._data.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return str(self._data.get("product_id_no") or "Unnamed Product")

    def get_translated_description(self, locale: str = "en") -> str:
        # 处理 Flask-Babel 返回的 Locale 对象
        if hasattr(locale, 'language'):
            locale = str(locale)
        locale = (locale or "en").lower()
        desc_keys = []
        if locale == "zh_cn":
            desc_keys = ["description", "description_zh", "description_cn", "desc"]
        elif locale == "ja":
            desc_keys = ["description_ja", "description", "desc"]
        elif locale == "es":
            desc_keys = ["description_es", "description", "desc"]
        else:
            desc_keys = [f"description_{locale}", "description", "desc"]

        for key in desc_keys:
            val = self._data.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return ""

def list_products(category: Optional[str] = None, page: int = 1, page_size: int = 20) -> List[ProductVM]:
    start = max(0, (int(page) - 1) * int(page_size))
    end = start + int(page_size) - 1
    query = extensions.supabase.table("product").select("*")
    
    if category:
        # 映射分类名称到 ID
        cat_map = {
            "Infrared Drones": 1,
            "Cargo Drones": 2,
            "Spray Drones": 3,
            "Payloads & Accessories": 4
        }
        cat_id = cat_map.get(category)
        if cat_id:
            query = query.eq("category_id", cat_id)
        
    resp = query.range(start, end).execute()
    items = getattr(resp, "data", []) or []
    return [ProductVM(d) for d in items]

def get_product(product_id: Any) -> Optional[ProductVM]:
    # 兼容整数 ID 和 字符串编号
    query = extensions.supabase.table("product").select("*")
    if isinstance(product_id, int) or (isinstance(product_id, str) and product_id.isdigit()):
        query = query.eq("id", int(product_id))
    else:
        query = query.eq("product_id_no", product_id)
        
    resp = query.limit(1).execute()
    items = getattr(resp, "data", []) or []
    if items:
        return ProductVM(items[0])
    return None
