# 实施计划：Web 界面开发（app/main.py）

## Context
创建 FastAPI 应用的主入口 `app/main.py`，实现 Web 界面和路由功能。用户通过浏览器访问工具，选择选题后生成笔记文案和封面图。

## 功能需求

### 1. 静态文件挂载
- 路径：`/static` → 映射到项目根目录
- 用途：访问生成的封面图、CSS、JS 等静态资源

### 2. Jinja2 模板配置
- 模板目录：`app/templates`
- 支持变量传递和 HTML 渲染

### 3. 路由设计

| 路由 | 方法 | 功能 | 传递变量 |
|------|------|------|----------|
| `/` | GET | 首页，显示选题列表 | topics, published_count, total_count |
| `/generate/{topic_idx}` | POST | 生成笔记和封面 | note_content, cover_url |
| `/output/{filename}` | GET | 返回生成的文件 | - |

## 实施步骤

### 1. 创建 app/main.py
导入必要模块：
- `FastAPI`, `Request`, `FileResponse` (fastapi)
- `StaticFiles` (fastapi.staticfiles)
- `Jinja2Templates` (fastapi.templating)

### 2. 路由实现

#### GET /
- 调用 `core.get_unpublished_topics()` 获取未发布选题
- 调用 `core.get_all_topics()` 获取所有选题（需新增此函数）
- 计算 published_count 和 total_count
- 渲染 `index.html`

#### POST /generate/{topic_idx}
- 调用 `core.generate_note_and_cover(topic_idx)`
- 成功：读取生成的 note.txt 内容，渲染 `preview.html`
- 失败：返回首页并显示错误信息

#### GET /output/{filename}
- 使用 `FileResponse` 返回文件

### 3. 创建前端模板

#### app/templates/index.html
- 显示选题列表
- 显示已发布/未发布统计
- 每个选题显示：痛点、人群、书籍、金句
- 提供"生成"按钮

#### app/templates/preview.html
- 显示生成的文案内容
- 显示生成的封面图
- 提供"复制文案"按钮
- 提供"返回列表"按钮

### 4. 新增 core.py 函数
需要新增 `get_all_topics()` 函数用于统计总数

## 关键文件

### 新建文件
- `app/main.py` - FastAPI 应用入口
- `app/templates/index.html` - 首页模板
- `app/templates/preview.html` - 预览页模板

### 修改文件
- `app/core.py` - 新增 `get_all_topics()` 函数

## 验证方法

1. 启动服务：`uvicorn app.main:app --reload`
2. 访问 http://127.0.0.1:8000
3. 检查首页是否正确显示选题列表
4. 点击"生成"按钮，检查是否能生成预览页面
5. 检查封面图是否正确显示

## 注意事项

1. 异常处理：所有路由都应处理可能出现的异常
2. 文件路径使用 `pathlib.Path`
3. 模板渲染使用 UTF-8 编码
4. 静态文件路径正确配置


用 Jinja2 语法写两个 HTML 文件：

1. app/templates/index.html：
- 标题：📚 小红书自动创作台
- 显示统计：已发布 {{ published_count }} / {{ total_count }} 篇
- 如果有 error，显示红色提示
- 遍历 topics，每条显示：
    {{ loop.index0 + 1 }}. {{ topic.痛点 }}
    👥 {{ topic.人群 }} | 📖 {{ topic.书籍 }}
    表单 POST 到 /generate/{{ loop.index0 }}，按钮文字“✨ 生成笔记”
- 无选题时显示“✅ 所有选题已完成！”

样式要求：
- 使用小红书品牌色 #ff2442
- 卡片式布局，圆角，阴影轻
- 手机友好（max-width: 800px, margin: auto）
- 字体：系统默认 sans-serif

2. app/templates/preview.html：
- 标题：✅ 生成成功！
- 显示封面：<img src="{{ cover_url }}" style="width:100%; max-width:360px; border-radius:16px;">
- 显示文案：<pre style="background:white; padding:20px; border-radius:12px; white-space:pre-wrap;">{{ note_content }}</pre>
- 三个按钮（居中）：
    <a href="/">🏠 返回首页</a>
    <a href="{{ cover_url }}" download="cover.jpg">📥 下载封面</a>
    <a href="/output/note.txt" download="note.txt">📄 下载文案</a>

整体风格：清新、简洁、粉白配色。