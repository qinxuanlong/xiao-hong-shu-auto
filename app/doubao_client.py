"""
豆包 AI 图片生成客户端
使用豆包的 Seedream 模型生成封面图
"""

import io
from pathlib import Path
from typing import Optional

import requests
from PIL import Image


def generate_image_with_doubao(
    prompt: str,
    api_key: str,
    model: str = "doubao-seedream-4-5-251128",
    width: int = 1080,
    height: int = 1440
) -> Optional[Image.Image]:
    """
    使用豆包 Seedream 模型生成图片

    Args:
        prompt: 图片生成提示词
        api_key: 豆包 API Key
        model: 模型名称，默认为 doubao-seedream-4-5-251128
        width: 图片宽度
        height: 图片高度

    Returns:
        PIL Image 对象，失败返回 None
    """
    endpoint = "https://ark.cn-beijing.volces.com/api/v3/images/generations"

    # 根据尺寸选择 size 参数
    # 2K: 1440x2048, 1K: 1024x1024
    if width >= 1000 or height >= 1000:
        size = "2K"
    else:
        size = "1K"

    try:
        # 构造请求
        payload = {
            "model": model,
            "prompt": prompt,
            "sequential_image_generation": "disabled",
            "response_format": "url",
            "size": size,
            "stream": False,
            "watermark": True
        }

        response = requests.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        # 检查响应结构
        # 豆包返回格式: {"data": [{"url": "..."}, ...]}
        if "data" not in result or not result["data"]:
            print(f"豆包 API 返回无 data: {result}")
            return None

        # 获取第一张图片的 URL
        image_url = result["data"][0].get("url")
        if not image_url:
            print(f"豆包 API 返回无图片 URL: {result}")
            return None

        # 下载图片
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()

        # 转换为 PIL Image
        image = Image.open(io.BytesIO(img_response.content))

        # 调整尺寸到目标尺寸
        if image.width != width or image.height != height:
            image = image.resize((width, height), Image.Resampling.LANCZOS)

        return image

    except Exception as e:
        print(f"豆包图片生成失败: {str(e)}")
        return None
