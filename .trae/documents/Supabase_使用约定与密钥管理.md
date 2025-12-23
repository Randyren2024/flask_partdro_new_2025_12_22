# Supabase 使用约定与密钥管理

- 在后端使用 `SUPABASE_ANON_KEY` 配合 RLS；仅当需要管理操作时使用 `SUPABASE_SERVICE_ROLE_KEY`
- 不在前端或公共仓库暴露任何密钥；生产环境通过系统环境变量注入
- 统一通过 `supabase_client.py` 获取客户端，避免分散初始化与重复配置
- 采用最小权限与策略优先：先创建 RLS 策略，再开放读写路径
- 版本管理：`supabase` 2.x，`Werkzeug` 3.x，与 `Flask` 3.x 兼容
- 异常处理：所有数据库/存储操作返回值需判空与错误分支
