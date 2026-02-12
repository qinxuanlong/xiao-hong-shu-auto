"""
修复书名号缺失问题
"""
import pandas as pd
from pathlib import Path
import sys
import io

# 设置控制台编码为 UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 项目根目录
project_root = Path(__file__).parent.parent
topics_csv_path = project_root / "data" / "topics.csv"

# 读取数据
df = pd.read_csv(topics_csv_path, encoding="utf-8")

# 修复书名号
fixed_count = 0

for idx, row in df.iterrows():
    book_name = str(row["书籍"])
    # 移除现有的书名号（如果有的话）
    clean_name = book_name.replace("《", "").replace("》", "")
    # 重新添加书名号
    fixed_name = f"《{clean_name}》"
    if book_name != fixed_name:
        df.at[idx, "书籍"] = fixed_name
        fixed_count += 1
        print(f"修复: {book_name} -> {fixed_name}")

# 保存
df.to_csv(topics_csv_path, index=False, encoding="utf-8-sig")

print(f"\n✅ 完成！修复了 {fixed_count} 条记录")
