"""
小红书创作助手 - FastAPI 主应用入口
"""

from pathlib import Path
import sys

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse

# 添加 app 目录到 Python 路径
app_dir = Path(__file__).parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# 导入核心模块
try:
    from core import (
        load_config,
        get_unpublished_topics,
        generate_note_and_cover
    )
except ImportError:
    # 如果 core.py 还不存在，创建占位函数
    def load_config():
        return {}

    def get_unpublished_topics():
        import pandas as pd
        return pd.DataFrame()

    def generate_note_and_cover(topic_idx: int):
        return (None, None, "core module not implemented")

# 创建 FastAPI 应用
app = FastAPI(
    title="小红书创作助手",
    description="本地内容创作自动化工具",
    version="1.0.0"
)

# 挂载静态文件（映射到项目根目录）
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent.parent)), name="static")

# 配置 Jinja2 模板
templates = Jinja2Templates(directory=str(app_dir / "templates"))


@app.get("/")
async def index(request: Request):
    """
    首页 - 显示选题列表
    """
    try:
        # 获取未发布的选题
        unpublished_topics = get_unpublished_topics()
        topics_list = unpublished_topics.to_dict("records") if not unpublished_topics.empty else []

        # 计算统计信息
        # 需要从 core 获取所有选题来计算总数
        from pandas import read_csv
        topics_csv_path = Path(__file__).parent.parent / "data" / "topics.csv"
        if topics_csv_path.exists():
            all_topics = read_csv(topics_csv_path, encoding="utf-8")
            total_count = len(all_topics)
            published_count = len(all_topics[all_topics["status"] == "published"])
        else:
            total_count = 0
            published_count = 0

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "topics": topics_list,
                "published_count": published_count,
                "total_count": total_count
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "topics": [],
                "published_count": 0,
                "total_count": 0,
                "error": f"加载失败: {str(e)}"
            }
        )


@app.post("/generate/{topic_idx}")
async def generate(request: Request, topic_idx: int):
    """
    生成笔记和封面
    """
    try:
        note_path, cover_path, status = generate_note_and_cover(topic_idx)

        if status != "success":
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "topics": get_unpublished_topics().to_dict("records"),
                    "published_count": 0,
                    "total_count": 0,
                    "error": f"生成失败: {status}"
                }
            )

        # 读取生成的文案内容
        with open(note_path, "r", encoding="utf-8") as f:
            note_content = f.read()

        # 封面图 URL
        cover_filename = Path(cover_path).name
        cover_url = f"/static/output/covers/{cover_filename}"

        return templates.TemplateResponse(
            "preview.html",
            {
                "request": request,
                "note_content": note_content,
                "cover_url": cover_url
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "topics": get_unpublished_topics().to_dict("records"),
                "published_count": 0,
                "total_count": 0,
                "error": f"生成失败: {str(e)}"
            }
        )


@app.get("/output/{filename}")
async def get_output_file(filename: str):
    """
    返回生成的文件
    """
    try:
        output_dir = Path(__file__).parent.parent / "output"
        file_path = output_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        return FileResponse(
            path=str(file_path),
            media_type="application/octet-stream"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件读取失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    config = load_config()
    host = config.get("app", {}).get("host", "127.0.0.1")
    port = config.get("app", {}).get("port", 8000)

    uvicorn.run(app, host=host, port=port)
