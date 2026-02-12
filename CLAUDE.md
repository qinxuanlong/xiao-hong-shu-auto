# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个**小红书内容创作自动化助手** - 一个本地 Web 工具，帮助内容创作者生成笔记草稿和封面图。该工具完全在本地运行，不与小红书平台 API 交互（因为平台未开放公开 API）。

**核心设计原则：** 此工具仅作为内容创作辅助工具。所有发布必须由用户手动完成，以避免被平台判定为机器人而导致账号封禁。

## 架构设计

项目采用分层 FastAPI 架构：

```
app/
├── main.py              # FastAPI 应用入口，路由注册
├── api/                 # HTTP 路由层（generate, cover, topics, export）
├── services/            # 业务逻辑层
├── core/                # 核心功能层（通义千问客户端、验证器）
├── models/              # Pydantic 数据模型
├── templates/           # Jinja2 HTML 模板
├── static/              # CSS 和 JavaScript
└── utils/               # 工具函数
```

**数据流程：**
1. 用户从 `data/topics.csv` 选择选题
2. 系统从 `data/templates/` 加载提示词模板
3. 通过 Dashscope SDK 调用通义千问 AI 生成内容
4. 使用 Pillow 从 `assets/backgrounds/` 和 `assets/fonts/` 生成封面图
5. 输出保存到 `output/drafts/` 和 `output/covers/`
6. 用户手动复制内容并在小红书发布

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY

# 启动开发服务器
uvicorn app.main:app --reload

# 运行测试（待实现）
pytest
```

## 关键配置文件

- `config.json` - 应用配置（路径、AI 参数、封面尺寸）
- `.env` - 环境变量（QWEN_API_KEY）
- `data/topics.csv` - 选题数据库，字段：id,痛点,人群,书籍,金句,状态,创建时间

## 技术栈

- **Web 框架：** FastAPI + Uvicorn
- **AI：** Dashscope（通义千问 SDK）
- **图片处理：** Pillow (PIL)
)
- **数据处理：** Pandas, CSV
- **数据模型：** Pydantic
- **模板引擎：** Jinja2

## 功能边界

**可自动化（✅）：**
- 内容生成（标题、正文）
- 封面图生成（背景图上的文字叠加）
- 通过 CSV 管理选题
- 内容验证和格式化

**必须手动（❌）：**
- 所有平台交互（登录、发布、上传）
- 评论、点赞、关注
- 任何定时自动发布功能

完整安全指南请参考 `docs/小红书自动化功能边界.md`

## 开发注意事项

1. **不要实现平台自动化** - 禁止使用 Selenium、Puppeteer 或 API 爬取
2. **所有文件操作使用 pathlib.Path** 以确保跨平台兼容性
3. **中文编码：** 文件读写始终使用 `encoding="utf-8"`
4. **输出结构：** 生成的文件保存到 `output/`，命名格式为 `note_{idx}.txt` 和 `cover_{idx}.jpg`
5. **选题状态：** 生成内容后，需将 CSV 中对应选题的状态更新为 "published"
