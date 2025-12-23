# 迁移总体思路
- 在现有 `app.py` 完全可运行的前提下，小步拆分：先工厂与扩展，再蓝图与入口，最后移除全局 `app`
- 每一步包含明确的验证点与可回滚方案

## 步骤 1：建立骨架并保留现状
- 在 `d:\partdro.com\flask_partdro_new_2025_12_22` 新增：
  - `app/__init__.py`、`app/extensions.py`
  - `app/blueprints/main/__init__.py`、`app/blueprints/main/views.py`
  - `config.py`、`wsgi.py`
- 不改动 `app.py`，确保原启动方式仍可运行
- 验证点：原入口启动无变化

## 步骤 2：配置类与工厂函数
- `config.py` 定义：`DevelopmentConfig`、`TestingConfig`、`ProductionConfig`
- `app/__init__.py` 添加工厂：
```
from flask import Flask
import os
from .extensions import db

def create_app(config_object="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-me")
    db.init_app(app)
    return app
```
- 验证点：`from app import create_app; app = create_app()` 能创建实例（不运行服务）

## 步骤 3：扩展改为懒初始化
- `app/extensions.py`：
```
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```
- 将 `app.py` 的 `db = SQLAlchemy(app)` 改成在各模型文件引用 `from app.extensions import db`
- 在工厂中 `db.init_app(app)` 完成绑定
- 验证点：数据库相关视图在旧入口仍可用；工厂创建实例不抛错

## 步骤 4：蓝图迁移第一批路由
- `app/blueprints/main`：
```
# __init__.py
from flask import Blueprint
bp = Blueprint("main", __name__)

# views.py
from . import bp
@bp.route("/")
def index():
    return "OK"
```
- 在工厂注册：
```
from .blueprints.main import bp as main_bp
app.register_blueprint(main_bp)
```
- 从 `app.py` 剪切首页路由到蓝图，保留其余路由暂不迁移
- 验证点：通过工厂运行首页可达；旧入口其余路由仍可达

## 步骤 5：运行入口切换（开发环境）
- PowerShell 设置并运行：
  - `$env:FLASK_APP="app:create_app"`
  - `$env:FLASK_ENV="development"`
  - `flask run`
- 验证点：首页与已迁移路由在工厂入口正常；未迁移路由仍可在旧入口正常

## 步骤 6：环境变量与密钥
- `.env` 中的 `FLASK_SECRET_KEY=your_flask_secret_key` 替换为高强度值
  - 生成示例：`python - <<"PY"
import secrets
print(secrets.token_hex(32))
PY`
- 本地通过 `python-dotenv` 或 PowerShell `$env:FLASK_SECRET_KEY` 注入；生产仅用系统环境
- 验证点：工厂入口读取到非默认密钥

## 步骤 7：分批迁移剩余路由与中间件
- 依次迁移模块：认证/账户 → 商品目录 → 订单 → 管理后台 → API
- 为每批添加蓝图与前缀：`/admin`、`/api/v1`
- 将 `before_request`、`errorhandler` 移入工厂或所属蓝图
- 验证点：每批迁移后做路由与权限回归；无 404/循环导入

## 步骤 8：模型与迁移体系
- 统一模型引用 `app.extensions.db`，使用 `Flask-Migrate` 管理迁移
- 在工厂中初始化 `Migrate(app, db)`
- 验证点：迁移脚本生成与升级/降级正常

## 步骤 9：测试与 CI 改造
- `pytest` 使用工厂创建 `app` fixture 与独立 `app_context`
- 针对蓝图的路由、权限、数据库操作编写用例
- 验证点：本地与 CI 均通过

## 步骤 10：生产入口与收尾
- `wsgi.py`：
```
from app import create_app
app = create_app("config.ProductionConfig")
```
- 部署改用 `wsgi.py`；确认日志、错误处理与健康检查
- 在所有路由迁移完成且测试稳定后，移除旧 `app.py` 的全局 `app`
- 验证点：功能等价、监控正常、无隐性回归

## 回滚策略
- 每步仅迁移小批量路由；若异常，恢复上一版本并缩小迁移粒度
- 保留旧入口直到全部模块迁移与测试完成