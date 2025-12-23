## 依赖校对与建议

* 你当前的依赖：

  * `Flask==3.0.0`

  * `supabase==1.0.3`

  * `python-dotenv==1.0.0`

  * `python-multipart==0.0.6`

  * `Werkzeug==2.3.7`

  * `gunicorn==21.2.0`

* 建议调整：

  * 将 `supabase` 升级到 2.x（如 `supabase==2.27.0` 或 `supabase>=2.27.0,<3`），以获得最新 API 与修复［PyPI: supabase 2.27.0］(<https://pypi.org/project/supabase/>)

  * 与 `Flask==3.0.0` 对齐 `Werkzeug` 至 3.x（或不显式固定，让 pip 自动解析），避免 2.3.7 的潜在不兼容［Flask 变更记录中提到最低版本提升与 3.x 生态］(<https://flask.palletsprojects.com/en/stable/changes/>)

  * `python-multipart` 对 Flask 并非必需（Flask/Werkzeug已内置 multipart 解析），如无特殊用途可移除，减少冲突面

  * `gunicorn` 仅在 Linux/容器部署生效；Windows 开发环境不会用到，如部署目标为 Linux 可保留

* 推荐 requirements.txt（示例）：

  * `Flask==3.0.0`

  * `supabase>=2.27.0,<3`

  * `python-dotenv==1.0.0`

  * （可选，仅 Linux 部署）`gunicorn==21.2.0`

  * 不固定 `Werkzeug` 或改为 `Werkzeug>=3.0.0`；移除 `python-multipart`

## 环境变量与安全

* 在 `.env` 增加：

  * `SUPABASE_URL`

  * `SUPABASE_ANON_KEY`（首选，配合 RLS 读写）

  * `SUPABASE_SERVICE_ROLE_KEY`（可选，仅服务端管理操作时用，严禁暴露到客户端）

* 将 `FLASK_SECRET_KEY` 设置为强随机值；生产环境通过系统环境注入而非提交到仓库

## 客户端初始化与结构

* 新增 `supabase_client.py`：读取环境变量，`from supabase import create_client` 并导出共享 `Client`

* 在 Flask 应用入口（如 `app.py` 或工厂）调用 `load_dotenv()` 加载 `.env`

* 业务层封装 Supabase 读写（视图调用服务层），保持解耦

## 典型用法

* 查询：`supabase.table("instruments").select("*").execute()`

* 插入：`supabase.table("instruments").insert({...}).execute()`

* 过滤：链式 `eq/neq/gt/...` 后 `execute()`

* 鉴权：`supabase.auth.sign_up / sign_in_with_password / sign_out`

* 存储：`supabase.storage.from_(bucket).upload / download`

* 文档参考：［Python 客户端总览］(<https://supabase.com/docs/reference/python/introduction>)

## 替代 CLI 的工作流

* 不再使用 `supabase init/start` 本地容器；改为直接访问线上 Supabase 项目

* 如需管理 schema/策略：使用 Dashboard 的 SQL Editor 或在 CI 中跑迁移脚本

* 离线本地栈将不再提供（CLI+Docker 才具备），本方案主打“线上统一环境”

## 验证方案

* 添加 `/health/db` 路由：执行一次只读查询并返回记录计数，验证连接与凭据

* 可再添加一次受控插入并查询确认（测试后清理）

## 执行步骤（确认后我将进行）

1. 更新 `requirements.txt`（升级 `supabase`，对齐/放宽 `Werkzeug`，移除 `python-multipart`）
2. 配置 `.env` 所需键并强化 `FLASK_SECRET_KEY`
3. 编写 `supabase_client.py` 并在应用中统一引入
4. 添加示例路由与服务方法，运行并验证查询/写入/鉴权基本路径
5. 记录使用约定与密钥管理注意事项

