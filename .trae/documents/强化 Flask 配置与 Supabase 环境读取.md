## 目标
- 提升 config.py 的健壮性：按环境加载 .env、强制生产环境密钥、统一 Supabase 键名优先级
- 让 supabase_client 复用 Config，避免重复读取与分散逻辑

## 改动
- config.py
  - 仅在未设置 `FLASK_SKIP_DOTENV=1` 时加载 `.env`
  - `SECRET_KEY`：生产环境缺失时报错，开发环境使用安全占位
  - `SUPABASE_URL` 必填校验
  - `SUPABASE_KEY` 按优先级读取：`SUPABASE_ANON_KEY` → `SUPABASE_KEY` → `SUPABASE_PUBLISHABLE_KEY` → `SUPABASE_SERVICE_ROLE_KEY`
- supabase_client.py
  - 不再独立 `load_dotenv`
  - 直接从 `Config` 读取 `SUPABASE_URL` 与 `SUPABASE_KEY`

## 验证
- 停止并重启开发服务器
- 访问 `http://127.0.0.1:5000/health/db` 验证连接与返回

## 交付
- 代码变更生效，无注释；现有路由与依赖保持兼容