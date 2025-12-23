## 目标
1.  **创建本地专用调试页面**：位于 `/debug`，仅在非生产环境（`FLASK_ENV!=production`）下可访问。
2.  **集成 DeepSeek 翻译**：用户输入产品英文名称/描述，后端调用 DeepSeek API 自动生成日/西等多语言版本。
3.  **Supabase 状态与操作**：展示连接状态，提供图片上传与产品数据写入功能（支持 SQL 预览或直接 API 写入）。

## 实现方案

### 1. 调试蓝图 `partdro/blueprints/debug`
-   **路由**：
    -   `GET /debug/`: 渲染调试面板，包含状态检查、操作表单。
    -   `POST /debug/translate`: 接收 `{name, description}`，调用 DeepSeek API 返回 `{name_ja, description_ja, ...}`。
    -   `POST /debug/upload_product`: 接收完整产品数据与图片，上传图片到 Supabase Storage，并将多语言数据写入 `product` 表。
-   **环境限制**：使用 `before_request` 钩子，若 `app.config['ENV'] == 'production'` 或未设置调试标志，则拦截并返回 404/403。

### 2. DeepSeek API 集成
-   **配置**：在 `config.py` 中读取 `DEEPSEEK_API_KEY`。
-   **服务**：创建 `partdro/services/ai.py`，封装 `translate_product_info(name, desc)` 函数。
    -   Prompt 策略：一次性请求生成 JSON 格式的多语言结果，包含 `ja` (日语), `es` (西语) 等。

### 3. 前端调试页 `templates/debug.html`
-   **状态区**：显示 Supabase 连接是否正常（ping `product` 表）。
-   **表单区**：
    -   输入：产品英文名、英文描述、landing_page ID、图片文件。
    -   动作：“AI 一键翻译”按钮（异步请求 `/debug/translate` 填充表单）。
    -   动作：“提交到数据库”按钮（上传图片 + 写入数据）。
-   **SQL 预览区**（可选）：显示生成的 UPSERT SQL 供手动执行验证。

### 4. 依赖更新
-   `requirements.txt`: 添加 `openai` (DeepSeek 兼容 OpenAI SDK) 或 `requests` (直接调用)；现有 `httpx`/`requests` 已足够。

## 执行步骤
1.  **配置与依赖**：更新 `config.py` 支持 `DEEPSEEK_API_KEY`；确保 `FLASK_DEBUG` 或自定义标志可用。
2.  **AI 服务实现**：编写 `partdro/services/ai.py`，实现多语言翻译逻辑。
3.  **蓝图开发**：创建 `partdro/blueprints/debug`，实现路由与环境拦截。
4.  **前端实现**：编写 `templates/debug.html`，集成 AI 翻译与上传逻辑。
5.  **注册与验证**：在 `create_app` 注册蓝图；本地测试流程。

## 待确认事项
-   DeepSeek API Key 将从环境变量获取，本地需配置 `.env`。
-   产品图片上传将复用现有的 `partdro.services.storage.upload` 逻辑。

确认后，我将按此计划从 AI 服务与调试蓝图开始实现。