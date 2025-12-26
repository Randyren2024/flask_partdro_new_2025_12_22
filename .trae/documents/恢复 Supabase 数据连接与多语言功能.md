目前后端（Python/Flask）与 Supabase 的通讯逻辑是完全正常的，但是刚刚更新的**前端 HTML 模板尚未连接到这些数据**。

我们需要进行“重新接线”，将 Supabase 的数据注入到这些新的漂亮页面中。

### **Supabase 与页面的对接清单**

1.  **首页 (`index.html`)**
    *   **对接内容**：读取 `products` 表。
    *   **现状**：后端已查询数据，但前端缺少展示循环（`{% for product in products %}`）。
    *   **计划**：在“Why Choose Us”下方添加一个动态的“**Featured Drones**”板块，展示从 Supabase 获取的产品列表。

2.  **联系我们 (`contact.html`)**
    *   **对接内容**：写入 `partner_applications` 表。
    *   **现状**：表单外观已就绪，但提交按钮尚未连接到后端接口。
    *   **计划**：添加一段 JavaScript，将表单数据转换为 JSON 并发送到现有的 `/api/apply-partner` 接口，实现无刷新提交。

3.  **多语言支持 (Global Header)**
    *   **对接内容**：语言切换功能。
    *   **现状**：新的 `header.html` 丢失了语言切换器下拉菜单，且导航文字未包裹翻译标签 `{{ _(...) }}`。
    *   **计划**：恢复语言切换器（地球图标），并为所有静态文本添加多语言支持。

### **实施计划**

我将分三步修复这些连接：

1.  **修复 `header.html`**：
    *   添加语言切换下拉菜单（EN/中文/日语/西语）。
    *   为 "Home", "About", "Contact" 添加 `{{ _() }}` 标签。

2.  **修复 `index.html`**：
    *   插入产品展示循环代码，使用 Supabase 中的 `name`, `description`, `image_url` 渲染产品卡片。

3.  **修复 `contact.html`**：
    *   添加 AJAX 脚本，对接 `/api/apply-partner` 接口，确保表单提交能写入 Supabase。

您确认执行这个修复计划吗？