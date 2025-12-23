import httpx
from config import Config

def fetch_openapi_schema():
    url = f"{Config.SUPABASE_URL}/rest/v1/"
    headers = {
        "apikey": Config.SUPABASE_KEY,
        "Authorization": f"Bearer {Config.SUPABASE_KEY}",
        "Accept": "application/openapi+json",
    }
    resp = httpx.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()

def list_tables_from_openapi(openapi: dict):
    paths = openapi.get("paths", {})
    tables = []
    for p in paths.keys():
        if p.startswith("/"):
            name = p[1:].split("/")[0]
            if name and name not in tables:
                tables.append(name)
    return sorted(tables)

def list_columns_from_openapi(openapi: dict, table: str):
    paths = openapi.get("paths", {})
    node = paths.get(f"/{table}")
    # 直接从 components.schemas 读取（更稳）
    comp_props = (
        openapi.get("components", {})
        .get("schemas", {})
        .get(table, {})
        .get("properties", {})
    )
    if comp_props:
        return sorted(list(comp_props.keys()))
    # Swagger 2.0: definitions
    def_props = (
        openapi.get("definitions", {})
        .get(table, {})
        .get("properties", {})
    )
    if def_props:
        return sorted(list(def_props.keys()))
    if not node:
        return []
    # 尝试从 GET 响应的 schema 提取列
    get_op = node.get("get", {})
    response_content = (
        get_op.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    # 数组 → items → properties
    items = response_content.get("items", {})
    props = items.get("properties", {})
    if props:
        return sorted(list(props.keys()))
    # 处理 $ref 到 components.schemas
    ref = items.get("$ref")
    if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
        schema_name = ref.split("/")[-1]
        schema = (
            openapi.get("components", {})
            .get("schemas", {})
            .get(schema_name, {})
        )
        props = schema.get("properties", {})
        if props:
            return sorted(list(props.keys()))
    return []
