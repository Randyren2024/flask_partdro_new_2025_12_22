## 目标
- 首页 `index.html` 基于 `base.html`/`header.html`/`footer.html` 正常渲染。
- 产品详情页根据 Supabase `products.landing_page` 字段动态选择模板：
  - `s150_landing_page.html`
  - `test_s200_by_gemini.html`
- 路由与服务稳健，后续你只需优化前端模板即可。

## 路由设计
- `main` 蓝图新增：
  - `/` → 渲染首页：`templates/index.html`（提供必要上下文，如 `products`、`locale`）
  - `/products` → 产品列表页（可分页/按分类筛选，后续可扩展）
  - `/product/<int:product_id>` → 产品详情页：根据 `landing_page` 动态选模板
  - `/about`、`/terms-and-services`、`/privacy-policy` → 基础静态页（占位模板）

## 数据接口（Supabase）
- 在 `partdro/services/db.py` 增加：
  - `list_products(category: str | None, page: int, page_size: int)`
  - `get_product(product_id: int)`（返回含 `landing_page`、名称/描述/图片/分类等字段）
- 查询示例参考现有方式：`extensions.supabase.table("products").select("...").eq("id", product_id).single().execute()`（与 `instruments_count` 同风格，见 `services/db.py:3-5`）。

## 模板映射约定
- 约定映射表（可扩展）：
  - `s150` → `s150_landing_page.html`
  - `s200` → `test_s200_by_gemini.html`
- `products.landing_page` 存储键值（如 `s150`/`s200`）；详情路由按映射选择模板。
- 若无匹配，降级到通用模板或返回 404。

## 渲染与上下文
- 统一 `render_template` 上下文：`product`、`site_name`（已有，见 `partdro/context.py:1-4`）、`locale`。
- 首页与列表页使用 `list_products` 结果，首页可按分类切片以兼容现有 `index.html` 的分区展示。

## 健康与预检查
- 新增 `GET /health/products`：
  - 校验 `products` 表可达且至少返回字段包含 `landing_page`。
  - 失败时返回错误详情，便于部署自检（与 `schema_health` 一致，见 `main/routes.py:14-21`）。

## 验证方式
- 本地启动后访问：
  - `/` 查看首页渲染
  - `/products` 列表
  - `/product/<id>` 详情是否根据 `landing_page` 切换模板
  - `/health/products` 自检接口返回 `ok: true`

## 变更范围
- 代码：`partdro/blueprints/main/routes.py`、`partdro/services/db.py`
- 模板：复用既有 `s150_landing_page.html`、`test_s200_by_gemini.html`，必要时新增通用 `product_detail.html`。
- 文档：更新 `README.md` 路由与使用说明。

确认后，我将按上述步骤依次实现并进行本地验证，确保路由与 Supabase 数据接入稳定。