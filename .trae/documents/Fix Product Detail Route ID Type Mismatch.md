这是一个非常具体的类型错误，原因很明确。

**错误原因分析：**
1.  **前端代码**：在 `index.html` 中，链接生成的代码是：
    ```html
    <a href="{{ url_for('main.product_detail', product_id=product.product_id_no) }}" ...>
    ```
    这里使用的是 `product.product_id_no`，而这个字段在您的数据库中是字符串类型（例如 `'S200'`）。

2.  **后端路由定义**：在 `routes.py` 中，路由定义强制要求 `product_id` 为整数：
    ```python
    @main_bp.route("/product/<int:product_id>")  # <--- 这里限定了 int
    def product_detail(product_id: int):
    ```

3.  **冲突点**：当 Jinja2 试图为字符串 `'S200'` 生成 URL 时，Flask 的路由转换器发现它不符合 `<int:product_id>` 的规则（因为 `'S200'` 无法转换为整数），从而抛出了 `ValueError: invalid literal for int() with base 10: 'S200'`。

### 修复方案：

我们需要修改 `routes.py` 中的路由定义，使其能够接受字符串作为 ID（因为您的产品编号如 'S200' 显然是字符串）。

**修改计划：**
1.  将 `routes.py` 中的 `@main_bp.route("/product/<int:product_id>")` 修改为 `@main_bp.route("/product/<product_id>")`（移除 `int:` 约束，默认为 string）。
2.  同时更新 `product_detail` 函数的类型注解和内部逻辑，确保它能处理字符串类型的 `product_id`（实际上 `get_product` 函数内部已经处理了兼容性，所以只需改路由定义即可）。

请确认，我将执行此修复。