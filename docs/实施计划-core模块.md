# 实施计划：创建 app/core.py 核心模块

## Context
实现小红书创作助手的核心功能模块 `app/core.py`，该模块负责：
1. 读取配置文件
2. 管理选题数据
3. 生成笔记文案和封面图

这是项目的核心逻辑层，涉及配置管理、CSV 数据操作、AI 调用和图片处理。

## 实施步骤

### 1. 创建目录结构
创建以下必要的目录：
- `app/` - 主应用目录
- `data/` - 数据目录
- `data/templates/` - 模板目录
- `output/` - 输出目录
- `assets/fonts/` - 字体目录

### 2. 编写 app/core.py 模块
创建 `app/core.py` 文件，包含以下函数：

#### 2.1 模块导入
```python
from pathlib import Path
import json
import random
import pandas as pd
import dashscope
from dashscope import Generation
from PIL import Image, ImageDraw, ImageFont
```

#### 2.2 load_config()
- 路径：`Path(__file__).parent.parent / "config.json"`
- 使用 `json.load()` 读取
- 返回配置字典

#### 2.3 get_unpublished_topics()
- 读取 `data/topics.csv`
- 过滤条件：`status != "published"`
- 返回 DataFrame

#### 2.4 generate_note_and_cover(topic_idx: int)
完整流程：
1. 加载配置
2. 获取未发布选题，按索引选择
3. 读取 `data/personal_snippets.txt`，随机选择一条
4. 读取 `data/templates/prompt_template.txt`，填充占位符 `{痛点}{人群}{书籍}{金句}`
5. 调用 `dashscope.Generation.call(model="qwen-max", ...)` 生成文案
6. 替换文案中的 "真的救了我！" 为 "{随机语句} 真的救了我！"
7. 保存文案到 `output/note.txt`
8. 打开 `data/templates/cover_template.jpg`，用 Pillow 绘制标题
   - 字体从 config 读取
   - 字号 48
   - 白色文字 + 黑色描边 (stroke_width=2, stroke_fill="black")
9. 保存封面到 `output/cover.jpg`
10. 更新 CSV 中对应选题的 status 为 "published"
11. 返回 `(note_path, cover_path, "success")`

### 3. 创建示例数据文件（如果不存在）
- `data/topics.csv` - 示例选题数据
- `data/personal_snippets.txt` - 示例真人语句
- `data/templates/prompt_template.txt` - 示例提示词模板
- `data/templates/cover_template.jpg` - 示例封面背景

## 关键文件

### 新建文件
- `app/core.py` - 核心功能模块
- `app/__init__.py` - 包初始化文件

### 示例数据文件（如不存在）
- `data/topics.csv`
- `data/personal_snippets.txt`
- `data/templates/prompt_template.txt`
- `data/templates/cover_template.jpg`

## 验证方法

1. 检查文件是否正确创建
2. 检查语法是否正确（Python 导入检查）
3. 测试 `load_config()` 能否正确读取配置
4. 测试 `get_unpublished_topics()` 能否返回正确数据

## 注意事项

1. 所有文件路径使用 `pathlib.Path`
2. 文件读写使用 `encoding="utf-8"`
3. 异常处理：当 API 调用失败或文件不存在时返回错误信息
4. 确保 `.env` 文件中的 `QWEN_API_KEY` 已配置
