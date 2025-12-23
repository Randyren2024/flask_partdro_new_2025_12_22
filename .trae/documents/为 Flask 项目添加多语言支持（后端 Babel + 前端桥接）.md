## 现状梳理（Supabase 视角）
- 产品表：代码使用 `product` 表并已存在按语言列的访问约定：
  - `ProductVM.get_translated_name()` 与 `get_translated_description()` 会按 `name_{locale}`/`description_{locale}`→`name`/`description` 顺序回退，见 `partdro/services/db.py:35-51`。
  - 列表/详情数据来源：`partdro/services/db.py:56-60`、`63-67`。
- 其他表：`instruments`（计数健康检查，`db.py:4-6`）；健康检查还读取 `products.landing_page`，见 `partdro/blueprints/main/routes.py:83-94`。
- 语言传递：路由已读取并传入模板，见 `partdro/blueprints/main/routes.py:29`、`39`、`55`。

## 目标与范围
- 统一多语言：
  - UI 固定文案（导航、页脚、按钮、搜索框等）走后端 Babel；
  - 产品/营销内容（易变动）走 Supabase，沿用或规范化现有按语言列策略；
  - 支持资源链接按语言切换（图片/视频可选）。

## 方案选型与规则
- UI 固定文案：Babel（PO/编译）维护；改动需发布，性能最佳。
- 动态内容：Supabase；运营可直接改库生效，无需发布。
- 语言判定优先级：`?locale`→Cookie `lang`→`Accept-Language`；默认 `en`。

## Supabase 策略（与现有架构兼容）
- 继续支持“列按语言”模式：`product` 表保留/新增 `name_zh_cn`、`description_zh_cn` 等；服务端通过已有 `ProductVM` 自动选择。
- 规范化建议（可逐步实施）：新增归一化表以提升扩展性与避免列膨胀：
  - `product_translations(product_id, locale, field, content, updated_at)`，主键 `(product_id, locale, field)`；适合存放着陆页段落、优势、应用场景等结构化/JSON 内容。
  - `page_translations(page_slug, locale, content_json, updated_at)`，主键 `(page_slug, locale)`；适合非产品页（如首页区块文案）。
- 读取顺序：优先归一化表→无则回退到 `product` 的按语言列→再回退到英文原文。

## 模板与路由改造
- Babel 接入：在 `partdro/__init__.py:12-23` 的 `create_app()` 初始化 `Flask-Babel`，配置 `BABEL_DEFAULT_LOCALE='en'` 与翻译目录。
- 模板改造：
  - `templates/header.html:19-36`、`43` 把导航与占位包裹为 `{{ _('...') }}`；`base.html`、`footer.html`、`index.html` 同理。
  - `s150_landing_page.html` 与 `test_s200_by_gemini.html`：首屏标题/按钮走 Babel（SSR 立即可译），正文段落通过 Supabase 注入（按 `product_id + locale` 或 `page_slug + locale`）。
- 路由数据注入：在 `partdro/blueprints/main/routes.py:53-66` 的 `product_detail`，依据 `locale` 拉取对应翻译块（归一化表或列），将 `content_json` 传入模板；模板按键渲染（缺失键回退英文）。

## 资源多语种化
- 图片/视频链接可迁入 `assets_i18n(asset_key, locale, url)`（可选）；否则在翻译 JSON 中直接给出按语言的链接。
- 资源回退：当前语言无资源时使用英文/通用资源，避免 404。

## 翻译维护流程
- Babel：`pybabel extract -F babel.cfg -o messages.pot .` → `pybabel init -l zh_CN -d translations` → 翻译 → `pybabel compile -d translations`。
- Supabase：运营通过表更新对应 `locale` 的 `content_json` 或 `name_{locale}`/`description_{locale}`；上线即生效。

## 测试与验证
- 模板：带 `?locale=zh-CN` 检查 `header/footer/index` 文案中文；不带参数回退英文。
- 产品页：在 Supabase 写入 `product_translations` 的中文标题，刷新可见；删除后回退英文或列值。
- API 错误：将用户可见字符串改为 `_()` 并验证中英文响应（`partdro/blueprints/main/routes.py:11-14,18-23,83-94`、`partdro/errors.py`）。

## 交付项
- Babel 集成与模板改造（UI 层）。
- Supabase 读取逻辑：归一化表优先（若创建），否则按语言列；注入模板变量与回退策略。
- 语言切换 UI 与 Cookie 设置路由。
- 配置 `babel.cfg` 与 `translations/`（含 `zh_CN` 示例）。

## 迭代建议
- 首期不改动数据库结构，先利用现有 `product` 的按语言列与 `ProductVM` 的读取逻辑快速上线；
- 后续逐步引入 `product_translations`/`page_translations` 以支持更复杂的营销段落与资源多语；
- 随着归一化推进，把 `s150_landing_page.html` 的前端 `data-key` 迁至后端统一来源，减少双维护与前端替换成本。