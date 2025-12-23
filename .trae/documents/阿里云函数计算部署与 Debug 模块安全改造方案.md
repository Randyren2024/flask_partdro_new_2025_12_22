## 阿里云函数计算 (FC) 部署与 Debug 安全化方案

### 1. 架构策略
我们采用 **Monorepo（单体仓库）+ Custom Container（自定义容器）** 模式。
-   **代码库**：继续使用 `https://github.com/Randyren2024/flask_partdro_new_2025_12_22`。
-   **运行环境**：通过 Docker 镜像打包 Flask 应用，部署到阿里云 FC。
-   **Debug 模块**：不拆分，而是通过 **Access Key 鉴权** 机制，使其在生产环境中安全可用。

### 2. 实施步骤

#### Phase 1: 代码安全改造
为了让 `/debug` 页面在云端安全运行，我们将移除“仅开发环境可用”的硬限制，改为“仅持有密钥者可用”。
1.  **Config 更新**：在 `config.py` 中增加 `ADMIN_ACCESS_KEY`，从环境变量读取。
2.  **路由鉴权**：修改 `partdro/blueprints/debug/routes.py` 的 `before_request`，检查 URL 参数 `?key=...` 或 Session 是否匹配密钥。如果不匹配，返回 403。
3.  **注册逻辑**：修改 `partdro/__init__.py`，无条件注册 `debug_bp`（不再检查 `ENV != production`）。

#### Phase 2: 容器化构建
创建标准化的 Docker 构建文件，适配阿里云 FC。
1.  **Dockerfile**：
    -   Base Image: `python:3.10-slim`
    -   安装依赖：`pip install -r requirements.txt`
    -   启动命令：使用 `gunicorn` 启动 Flask 应用，监听 FC 指定端口（默认 9000）。
2.  **.dockerignore**：排除 `.git`, `.venv`, `__pycache__` 等。

#### Phase 3: CI/CD 自动化 (Github Actions)
配置 Github Action 自动部署流程。
1.  **Workflow 文件**：`.github/workflows/deploy-fc.yml`
2.  **流程**：
    -   `on: push to main`
    -   登录阿里云 ACR (Container Registry)。
    -   构建 Docker 镜像并推送。
    -   使用 `aliyun-fc-action` 或 `serverless-devs` 更新函数配置（更新镜像 tag）。

### 3. 使用方法
部署完成后，您可以通过以下方式访问调试页：
-   URL: `https://<您的FC域名>/debug/?key=<您的ADMIN_ACCESS_KEY>`
-   普通用户访问 `/debug/` 会被拒绝，确保安全。

我将立即开始执行 Phase 1 和 Phase 2 的代码修改。Phase 3 将为您生成 Workflow 模板文件。