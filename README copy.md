# 小红书内容创作自动化助手

一个本地 Web 工具，帮助内容创作者生成小红书笔记草稿和封面图。该工具完全在本地运行，不与小红书平台 API 交互（因为平台未开放公开 API）。

> **核心设计原则：** 此工具仅作为内容创作辅助工具。所有发布必须由用户手动完成，以避免被平台判定为机器人而导致账号封禁。

---

## 核心功能

- **AI 文案生成** - 根据选题自动创作吸引人的标题和正文
- **封面图自动生成** - 智能生成符合小红书规范的封面图（1080x1440）
- **选题管理** - 通过 CSV 文件轻松管理你的创作选题
- **预览功能** - 在发布前预览文案和封面效果
- **安全设计** - 所有内容在本地生成，发布需手动操作

---

## 安装步骤

### 1. 安装 Python

确保你的系统已安装 Python 3.9 或更高版本：

```bash
python --version
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的 DashScope API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
QWEN_API_KEY=your_qwen_api_key_here
```

申请 API Key：前往 [DashScope 控制台](https://dashscope.console.aliyun.com/apiKey)

### 4. 准备字体和背景图

**字体文件：**
- 将黑体字体文件（如 `simhei.ttf`）放入 `assets/fonts/` 目录

**背景图片：**
- 将背景图片（命名为 `bg_01.jpg`）放入 `assets/backgrounds/` 目录
- 推荐尺寸：1080x1440（3:4 比例）

### 5. 准备选题数据

在 `data/topics.csv` 中添加你的选题，格式如下：

```csv
痛点,人群,书籍,金句,status
总忍不住刷手机,上班族,《认知觉醒》,"模糊是焦虑的源头，清晰是行动的开始",unpublished
想搞副业但没方向,宝妈,《纳瓦尔宝典》,"用专长+杠杆=财富",unpublished
```

### 6. 启动应用

```bash
uvicorn app.main:app --reload
```

或直接运行：

```bash
python app/main.py
```

---

## 开始使用

启动成功后，在浏览器中打开：

```
http://localhost:8000
```

### 使用流程

1. **查看选题列表** - 首页显示所有未发布的选题
2. **点击"生成"按钮"** - 根据选题自动生成文案和封面
3. **预览效果** - 在预览页面查看生成的内容
4. **复制内容** - 将文案复制到剪贴板，下载封面图
5. **手动发布** - 打开小红书 App 或网页版，粘贴内容并发布

---

## 项目结构

```
auto/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── core.py              # 核心业务逻辑模块
│   └── templates/           # HTML 模板
│       ├── index.html       # 首页
│       └── preview.html     # 预览页
├── data/
│   ├── topics.csv           # 选题数据
│   ├── personal_snippets.txt # 真人语句库
│   └── templates/           # AI 提示词模板
│       └── prompt_template.txt
├── output/
│   ├── drafts/              # 生成的文案
│   └── covers/              # 生成的封面图
├── assets/
│   ├── fonts/               # 字体文件
│   ├── backgrounds/         # 背景图片
│   └── logos/               # 水印/Logo
├── config.json              # 配置文件
├── requirements.txt         # 依赖列表
├── .env.example             # 环境变量示例
└── README.md                # 本文档
```

---

## 配置说明

### config.json

```json
{
  "app": {
    "title": "小红书创作助手",
    "host": "127.0.0.1",
    "port": 8000,
    "debug": true
  },
  "qwen": {
    "api_key": "${QWEN_API_KEY}",
    "model": "qwen-max",
    "temperature": 0.7,
    "max_tokens": 2000
  },
  "paths": {
    "data_dir": "data",
    "output_dir": "output",
    "assets_dir": "assets",
    "topics_csv": "data/topics.csv",
    "personal_snippets": "data/personal_snippets.txt",
    "prompt_template": "data/templates/prompt_template.txt",
    "drafts_dir": "output/drafts",
    "covers_dir": "output/covers"
  },
  "cover": {
    "width": 1080,
    "height": 1440,
    "default_font": "assets/fonts/simhei.ttf",
    "default_background": "assets/backgrounds/bg_01.jpg",
    "font_size": 48,
    "text_color": "white",
    "stroke_color": "black"
  }
}
```

### AI 配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `model` | 使用的 AI 模型 | `qwen-max` |
| `temperature` | 随机性参数（0-1） | `0.7` |
| `max_tokens` | 最大生成 token 数 | `2000` |

---

## 功能边界

**可自动化：**
- 内容生成（标题、正文）
- 封面图生成（背景图上的文字叠加）
- 通过 CSV 管理选题
- 内容验证和格式化

**必须手动：**
- 所有平台交互（登录、发布、上传）
- 评论、点赞、关注
- 任何定时自动发布功能

---

## 技术栈

- **Web 框架：** FastAPI + Uvicorn
- **AI：** Dashscope（通义千问 SDK）
- **图片处理：** Pillow (PIL)
- **数据处理：** Pandas, CSV
- **数据模型：** Pydantic
- **模板引擎：** Jinja2

---

## 常见问题

### Q: 为什么不能自动发布？

A: 小红书等社交平台严禁使用自动化工具进行批量发布，违规操作会导致账号被限制或封禁。本工具采用"半自动"设计，确保账号安全。

### Q: 生成的文案风格可以自定义吗？

A: 可以！在 `data/templates/` 目录下修改提示词模板，调整 AI 的输出风格。

### Q: 如何更换封面背景？

A: 将新的背景图片（1080x1440）放入 `assets/backgrounds/` 目录，并修改 `config.json` 中的配置。

### Q: 生成速度慢怎么办？

A: 生成速度取决于网络连接和 API 响应时间。可以尝试：
- 检查网络连接
- 选择更快的 AI 模型（如 `qwen-turbo`）

---

## 免责声明

本工具仅用于内容创作辅助，不涉及平台自动化交互。用户需自行承担因违反平台规则导致的风险。建议以人工操作为主，工具为辅。

---

## 许可证

MIT License

---

祝创作愉快！
