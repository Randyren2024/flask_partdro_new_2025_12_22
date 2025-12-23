# PartDro Flask App (App Factory)

- 使用 Flask App Factory 模式，统一扩展与蓝图管理
- 后端集成 Supabase Python 客户端

## 环境准备
- 创建并激活虚拟环境
  - PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
  - CMD: `.\\.venv\\Scripts\\activate.bat`
- 安装依赖
  - `python -m pip install --upgrade pip`
  - `pip install -r requirements.txt`

## 环境变量
- 在项目根创建 `.env` 并设置：
  - `SUPABASE_URL=...`
  - `SUPABASE_KEY=...` 或 `SUPABASE_ANON_KEY=...`
  - `FLASK_SECRET_KEY=...`（生产必须设置强随机值）
- 生产环境设置：`FLASK_SKIP_DOTENV=1`，只用系统环境变量注入密钥

## 运行开发服务
- `flask --app partdro:create_app --debug run`
- 或 `python app.py`
- 健康检查：打开 `http://127.0.0.1:5000/health/db`
  - OpenAPI：`http://127.0.0.1:5000/health/schema`
  - Products：`http://127.0.0.1:5000/health/products`

## CLI 命令
- `flask health` 输出数据库健康计数

## 生产入口
- `gunicorn -w 2 "partdro.wsgi:app"`（Linux/容器）

## 结构
- 工厂入口：`partdro/__init__.py`
- 配置：`config.py`
- 扩展：`partdro/extensions.py`
- 蓝图：`partdro/blueprints/main`
- 服务：`partdro/services`
- 错误处理：`partdro/errors.py`
- 上下文处理器：`partdro/context.py`
- 日志：`partdro/logging.py`
- WSGI：`partdro/wsgi.py`

## 路由
- 页面
  - `/` 首页（模板：`templates/index.html`，依赖 `base/header/footer`）
  - `/products` 产品列表（支持 `?category=...&page=1&page_size=20`）
  - `/product/<id>` 产品详情（按 `products.landing_page` 动态选择模板）
    - 映射：`s150` → `s150_landing_page.html`，`s200` → `test_s200_by_gemini.html`
  - `/about` `/terms-and-services` `/privacy-policy`（占位 JSON）
- 存储
  - `POST /storage/buckets` 创建桶
  - `POST /storage/upload` 表单文件上传
  - `POST /storage/upload_text` 文本上传
  - `GET /storage/public_url` 获取公共 URL

## 模板说明
- 着陆页模板：`templates/s150_landing_page.html`、`templates/test_s200_by_gemini.html`
- 通过 Supabase `products.landing_page` 字段选择使用的模板键（示例：`s150` / `s200`）

## 验证
- 配置 `.env` 后启动开发服务
- 访问 `/health/products` 确认 `products` 表与 `landing_page` 字段可读
- 访问 `/product/<id>` 检查是否正确渲染到对应着陆页模板
