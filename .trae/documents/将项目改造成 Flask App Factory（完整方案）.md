## 现状评估
- 已具备工厂函数：`app.py:5-18` 的 `create_app()` 完成基础配置与路由
- 配置集中：`config.py:9-28` 提供环境加载与必填变量校验
- Supabase 客户端统一：`supabase_client.py:1-3` 复用 `Config` 初始化
- 仍缺：包化结构、蓝图拆分、错误处理、日志、上下文处理器、CLI 与测试、生产入口

## 目标结构
- 包化目录：`partdro/`（或 `app/`）
  - `__init__.py`：`create_app()` 与扩展注册
  - `config.py`：`BaseConfig/DevConfig/ProdConfig/TestConfig`
  - `extensions.py`：`supabase` 等扩展实例化与初始化
  - `blueprints/main/__init__.py`、`routes.py`：页面与 API 路由
  - `services/`：业务逻辑封装（数据库、存储、鉴权）
  - `templates/`、`static/`：模板与静态资源（可继续使用现有目录或迁移到包内）
  - `errors.py`：统一错误处理（404/500 等）
  - `context.py`：Jinja 上下文处理器与过滤器
  - `logging.py`：按环境的日志配置
  - `wsgi.py`：生产入口（Gunicorn/Waitress 等）
  - `cli.py`：自定义命令（例如数据种子、健康检查）
- 顶层文件：`requirements.txt`、`.env`、`pytest.ini`/`tests/`

## 配置与扩展
- 将 `config.py` 拆分为类：
  - `BaseConfig`：通用设置、必填校验（`SUPABASE_URL/KEY`）
  - `DevConfig`：`DEBUG=True`、本地 `.env` 自动加载
  - `ProdConfig`：强制 `SECRET_KEY`、跳过 `.env` 自动加载
  - `TestConfig`：测试相关开关
- `extensions.py`：
  - 定义 `supabase: Client | None` 与 `init_supabase(app)`，在工厂函数中调用
  - 未来可加入缓存、邮件、队列等扩展

## 蓝图与视图
- 新建 `main` 蓝图：将 `/health/db` 等路由迁移到 `blueprints/main/routes.py`
- 在工厂函数中注册蓝图：`app.register_blueprint(main_bp)`
- 路由仅调用 `services` 层，视图不直接触达客户端实例

## 模板与上下文
- `context.py`：
  - `@app.context_processor` 提供常用变量（如站点名、版本）
  - 注册自定义 Jinja 过滤器（日期、货币等）
- 模板目录：
  - 方案 A：沿用项目根的 `templates/`、`static/`
  - 方案 B：迁移到包内并在工厂中指定 `template_folder`、`static_folder`

## 错误与日志
- `errors.py`：
  - `@app.errorhandler(404/500)` 返回统一 JSON 或模板页
- `logging.py`：
  - `dictConfig` 基于环境加载（开发控制台、生产文件/结构化日志）

## 运行与入口
- 开发：`flask --app partdro:create_app --debug run`
- 生产：`wsgi.py` 暴露 `app = create_app()`，`gunicorn -w 2 'partdro.wsgi:app'`
- 环境变量：生产设置 `FLASK_SKIP_DOTENV=1`，仅系统环境注入密钥

## CLI 与测试
- `cli.py`：注册 `flask` 自定义命令（如 `flask health`, `flask seed`）
- 测试：
  - `tests/conftest.py` 提供 `app` 与客户端夹具
  - 路由与服务单元测试，验证 Supabase 读写与错误分支

## 迁移步骤
1. 创建包目录与文件骨架（`__init__.py`、`extensions.py`、`blueprints/main`、`services` 等）
2. 将 `create_app()` 与当前路由迁移到包内，注册蓝图与上下文处理器
3. 将 `supabase_client` 改为扩展初始化，移除全局副作用
4. 拆分配置类并按环境加载；更新入口与运行命令
5. 添加错误处理与日志配置
6. 编写 CLI 命令与基础测试用例
7. 更新文档与 README，说明启动方式与环境变量策略

## 验证
- 本地启动后访问现有页面与 `/health/db`
- 运行测试套件确保路由、服务、错误处理与日志均正常
- 在生产模拟环境启动 `wsgi.py`，验证入口与日志

## 交付
- 完成包化改造、蓝图拆分、扩展初始化、错误与日志、CLI 与测试，保持无注释、符合现有代码风格