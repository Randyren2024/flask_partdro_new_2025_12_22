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
    def category(self) -> Optional[str]:
        return self._data.get("category")

    @property
    def image_url(self) -> Optional[str]:
        return self._data.get("image_url")

    @property
    def landing_page(self) -> Optional[str]:
        lp = self._data.get("landing_page")
        if isinstance(lp, str):
            return lp.strip().lower()
        return None

    def get_translated_name(self, locale: str = "en") -> str:
        locale = (locale or "en").lower()
        name_keys = [f"name_{locale}", "name", "title"]
        for key in name_keys:
            val = self._data.get(key)
            if isinstance(val, str) and val.strip():
                return val
        return str(self._data.get("product_id_no") or "Unnamed Product")

    def get_translated_description(self, locale: str = "en") -> str:
        locale = (locale or "en").lower()
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
    # 分类过滤可在后续基于 category_id 或名称映射实现
    resp = query.range(start, end).execute()
    items = getattr(resp, "data", []) or []
    return [ProductVM(d) for d in items]

def get_product(product_id: int) -> Optional[ProductVM]:
    resp = extensions.supabase.table("product").select("*").eq("id", product_id).limit(1).execute()
    items = getattr(resp, "data", []) or []
    if items:
        return ProductVM(items[0])
    return None
