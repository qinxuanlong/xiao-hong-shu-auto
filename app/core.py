"""
小红书创作助手 - 核心业务逻辑模块
"""

import json
import random
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Any

import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import requests


def load_config() -> Dict[str, Any]:
    """
    读取 config.json 配置文件
    支持环境变量替换，如 ${QWEN_API_KEY}
    """
    project_root = Path(__file__).parent.parent
    config_path = project_root / "config.json"

    with open(config_path, "r", encoding="utf-8") as f:
        config_str = f.read()

    # 替换环境变量占位符
    load_dotenv()
    import os

    def replace_env_var(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))

    config_str = re.sub(r'\$\{(\w+)\}', replace_env_var, config_str)
    return json.loads(config_str)


def backup_existing_file(file_path: Path):
    """
    备份已存在的文件，添加时间戳

    Args:
        file_path: 文件路径
    """
    if not file_path.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path_str = str(file_path)
    name, ext = path_str.rsplit(".", 1)
    backup_path = Path(f"{name}_backup_{timestamp}.{ext}")

    shutil.copy2(file_path, backup_path)
    print(f"已备份文件: {backup_path.name}")


def get_all_topics() -> pd.DataFrame:
    """
    获取所有选题（用于统计）
    """
    project_root = Path(__file__).parent.parent
    topics_csv_path = project_root / "data" / "topics.csv"

    if not topics_csv_path.exists():
        return pd.DataFrame()

    return pd.read_csv(topics_csv_path, encoding="utf-8")


def get_unpublished_topics() -> pd.DataFrame:
    """
    获取未发布的选题列表
    """
    df = get_all_topics()

    if df.empty:
        return pd.DataFrame()

    # 筛选 status 不为 "published" 的记录
    if "status" in df.columns:
        return df[df["status"] != "published"]

    return df


def generate_note_and_cover(topic_idx: int) -> Tuple[str, str, str]:
    """
    生成笔记文案和封面图

    Args:
        topic_idx: 选题索引（在未发布列表中的位置）

    Returns:
        (note_path, cover_path, status)
    """
    project_root = Path(__file__).parent.parent
    config = load_config()

    # 获取未发布选题
    unpublished_topics = get_unpublished_topics()

    if unpublished_topics.empty:
        return (None, None, "没有待处理的选题")

    if topic_idx >= len(unpublished_topics):
        return (None, None, "选题索引超出范围")

    # 获取当前选题
    topic = unpublished_topics.iloc[topic_idx]

    # 1. 读取真人语句库
    snippets_path = project_root / "data" / "personal_snippets.txt"
    snippets = []
    if snippets_path.exists():
        with open(snippets_path, "r", encoding="utf-8") as f:
            snippets = [line.strip() for line in f if line.strip()]

    random_snippet = random.choice(snippets) if snippets else ""

    # 2. 读取提示词模板并填充
    template_path = project_root / "data" / "templates" / "prompt_template.txt"
    with open(template_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    prompt = prompt_template.format(
        痛点=topic.get("痛点", ""),
        目标人群=topic.get("人群", ""),
        匹配书籍=topic.get("书籍", ""),
        书中金句=topic.get("金句", "")
    )

    # 3. 调用 DeepSeek API
    deepseek_config = config.get("deepseek", {})
    api_key = deepseek_config.get("api_key", "")
    model = deepseek_config.get("model", "deepseek-chat")
    temperature = deepseek_config.get("temperature", 0.7)
    max_tokens = deepseek_config.get("max_tokens", 2000)

    try:
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        if "choices" not in result or not result["choices"]:
            return (None, None, "AI 生成失败: 无返回内容")

        note_content = result["choices"][0]["message"]["content"]

    except Exception as e:
        return (None, None, f"AI 调用失败: {str(e)}")

    # 4. 替换"真的救了我！"
    if random_snippet and "真的救了我！" in note_content:
        note_content = note_content.replace(
            "真的救了我！",
            f"{random_snippet} 真的救了我！"
        )

    # 5. 保存文案
    drafts_dir = project_root / "output" / "drafts"
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # 获取选题唯一 ID 作为文件名
    topic_id = topic.get("id", topic_idx)
    note_filename = f"note_{topic_id}.txt"
    note_path = drafts_dir / note_filename

    # 备份现有文件（如果存在）
    if note_path.exists():
        backup_existing_file(note_path)

    with open(note_path, "w", encoding="utf-8") as f:
        f.write(note_content)

    # 6. 生成封面图
    covers_dir = project_root / "output" / "covers"
    covers_dir.mkdir(parents=True, exist_ok=True)

    cover_config = config.get("cover", {})
    doubao_config = config.get("doubao", {})

    try:
        # 提取标题（文案第一行，去掉 # 和空格）
        lines = note_content.strip().split("\n")
        title_line = lines[0] if lines else "笔记标题"
        title = title_line.lstrip("#").strip()

        # 构造图片生成提示词
        image_prompt = f"请为小红书笔记生成一张封面图。笔记标题是'{title}'，内容关于{topic.get('书籍', '书籍推荐')}。封面图应该符合小红书风格，色彩明亮，适合3:4竖屏比例（1080x1440）。"

        # 尝试使用豆包生成图片
        img = None
        if doubao_config.get("api_key"):
            try:
                from doubao_client import generate_image_with_doubao
                img = generate_image_with_doubao(
                    prompt=image_prompt,
                    api_key=doubao_config.get("api_key"),
                    model=doubao_config.get("model", "doubao-seedream-4-5"),
                    width=1080,
                    height=1440
                )
            except ImportError:
                print("未找到 doubao_client 模块，使用备用方案")
            except Exception as e:
                print(f"豆包图片生成失败: {str(e)}，使用备用方案")

        # 备用方案：使用本地背景图 + 文字叠加
        if img is None:
            font_path = project_root / cover_config.get("default_font", "assets/fonts/simhei.ttf")
            bg_path = project_root / cover_config.get("default_background", "assets/backgrounds/bg_01.jpg")

            # 打开背景图
            if bg_path.exists():
                img = Image.open(bg_path)
            else:
                # 如果没有背景图，创建一个渐变背景
                img = Image.new("RGB", (1080, 1440), color="#FFE4E1")

            # 调整尺寸
            img = img.resize((1080, 1440))
            draw = ImageDraw.Draw(img)

            # 设置字体
            try:
                if font_path.exists():
                    font = ImageFont.truetype(str(font_path), 48)
                else:
                    font = ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()

            # 计算文字位置（居中）
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            x = (1080 - text_width) // 2
            y = 300  # 距离顶部 300px

            # 绘制文字（白色文字 + 黑色描边）
            stroke_width = 2
            draw.text(
                (x, y),
                title,
                font=font,
                fill=cover_config.get("text_color", "white"),
                stroke_width=stroke_width,
                stroke_fill=cover_config.get("stroke_color", "black")
            )

        # 保存封面图
        cover_filename = f"cover_{topic_id}.jpg"
        cover_path = covers_dir / cover_filename

        # 备份现有文件（如果存在）
        if cover_path.exists():
            backup_existing_file(cover_path)

        img.save(str(cover_path), "JPEG", quality=95)

    except Exception as e:
        return (note_path, None, f"封面生成失败: {str(e)}")

    # 7. 更新 topics.csv 状态
    topics_csv_path = project_root / "data" / "topics.csv"
    all_topics = pd.read_csv(topics_csv_path, encoding="utf-8")

    # 找到匹配的行（通过 id）
    topic_df = all_topics[all_topics["id"] == topic_id]

    if not topic_df.empty:
        idx = topic_df.index[0]
        all_topics.at[idx, "status"] = "published"
        all_topics.to_csv(topics_csv_path, index=False, encoding="utf-8")

    return (note_path, cover_path, "success")
