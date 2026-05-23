"""将所有植物 PNG 图片转为 WebP 格式，并生成植物数据 JSON"""
import json
import os
import re
from pathlib import Path
from PIL import Image

BASE_DIR = Path(r"E:\植物")
OUTPUT_DIR = BASE_DIR / "img"
MAX_SIZE = 800  # 最大边长（像素）
WEBP_QUALITY = 80

OUTPUT_DIR.mkdir(exist_ok=True)

plant_data = []  # [{name: "紫唇花", images: ["img/紫唇花/1.webp", ...]}]

for folder in sorted(BASE_DIR.iterdir()):
    if not folder.is_dir():
        continue
    if folder.name in ("img", "__pycache__"):
        continue

    # 提取植物名
    raw_name = folder.name
    plant_name = re.sub(r"^淘宝店【i素材管家】", "", raw_name)

    png_files = sorted(folder.rglob("*.png"))
    if not png_files:
        continue

    # 创建输出子文件夹
    safe_folder = plant_name
    plant_out = OUTPUT_DIR / safe_folder
    plant_out.mkdir(exist_ok=True)

    images = []
    for i, png_path in enumerate(png_files):
        out_name = f"{i + 1}.webp"
        out_path = plant_out / out_name

        try:
            img = Image.open(png_path).convert("RGB")
            w, h = img.size
            if max(w, h) > MAX_SIZE:
                ratio = MAX_SIZE / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            img.save(out_path, "WEBP", quality=WEBP_QUALITY)
            size_kb = out_path.stat().st_size / 1024
            images.append(f"img/{safe_folder}/{out_name}")
            print(f"  [{plant_name}] {out_name} ({size_kb:.0f} KB)")
        except Exception as e:
            print(f"  [错误] {png_path}: {e}")

    if images:
        plant_data.append({"name": plant_name, "images": images})
        print(f"[完成] {plant_name}: {len(images)} 张")

# 写入数据文件
data_js_path = BASE_DIR / "plant_data.js"
with open(data_js_path, "w", encoding="utf-8") as f:
    f.write("// 自动生成，请勿手动编辑\n")
    f.write("const PLANT_DATA = ")
    json.dump(plant_data, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print(f"\n全部完成！共 {len(plant_data)} 种植物，数据文件: {data_js_path}")

# 统计输出文件夹大小
total = sum(
    f.stat().st_size
    for f in OUTPUT_DIR.rglob("*.webp")
)
print(f"输出总大小: {total / 1024 / 1024:.1f} MB")
