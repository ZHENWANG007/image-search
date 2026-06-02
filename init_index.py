import requests
import json
import time
import numpy as np
from PIL import Image
from io import BytesIO
from typing import List, Dict
from config import (
    RELIC_API_BASE,
    PAGE_SIZE,
    HEADERS,
    INDEX_PATH,
    METADATA_PATH
)
from feature_extractor import get_extractor
from faiss_index import get_index
from database import init_database, insert_many_relics, get_all_relics

def fetch_all_relics() -> List[Dict]:
    relics = []
    page = 1
    while True:
        url = f"{RELIC_API_BASE}?page={page}&pageSize=100"
        try:
            resp = requests.get(url, timeout=10, headers=HEADERS)
            print(f"第{page}页状态码: {resp.status_code}")
            if resp.status_code != 200:
                print(f"请求失败: {resp.status_code}")
                break

            data = resp.json()
            print(f"API 返回完整数据: {json.dumps(data, ensure_ascii=False, indent=2)}")

            # 兼容多种返回结构（关键修复）
            records = []
            if "data" in data and isinstance(data["data"], dict):
                records = data["data"].get("records", [])
            elif isinstance(data, list):
                records = data
            elif "records" in data:
                records = data["records"]

            if not records:
                print("当前页无数据，结束拉取")
                break

            relics.extend(records)
            print(f"已拉取 {len(relics)} 条文物")

            # 最多拉100条防止卡死
            if len(relics) >= 100:
                relics = relics[:100]
                break

            page += 1
        except Exception as e:
            print(f"请求异常: {e}")
            break
    return relics

def download_image(url: str, max_retries: int = 3) -> bytes | None:
    for retry in range(max_retries):
        try:
            resp = requests.get(url, timeout=10, stream=True)
            resp.raise_for_status()
            img_bytes = resp.content
            with Image.open(BytesIO(img_bytes)) as img:
                img.load()
                if img.mode != "RGB":
                    img = img.convert("RGB")
                    buf = BytesIO()
                    img.save(buf, format="JPEG")
                    img_bytes = buf.getvalue()
            return img_bytes
        except Exception as e:
            print(f"图片下载失败 {url} 第{retry+1}次: {e}")
            time.sleep(0.5)
    return None

def build_index():
    init_database()
    print("1. 拉取文物列表...")
    relics = fetch_all_relics()

    if not relics:
        print("未获取到文物数据，请检查接口配置")
        return

    for item in relics:
        item.setdefault("popularity", 0)
        item.setdefault("createTime", "")
        item.setdefault("updateTime", "")

    insert_many_relics(relics)
    print(f"已写入数据库 {len(relics)} 条")

    extractor = get_extractor()
    vectors = []
    metadata_list = []
    failed = 0

    print("2. 提取图片特征...")
    for idx, relic in enumerate(relics):
        try:
            if idx % 10 == 0:
                print(f"进度：{idx+1}/{len(relics)} 成功:{len(vectors)} 失败:{failed}")

            img_url = relic.get("imageUrl") or relic.get("imagePath")
            if not img_url:
                failed += 1
                continue

            img_bytes = download_image(img_url)
            if not img_bytes:
                failed += 1
                continue

            vec = extractor.extract(img_bytes)
            vectors.append(vec)

            metadata_list.append({
                "objectId": relic["objectId"],
                "title": relic["title"],
                "period": relic.get("period", ""),
                "type": relic.get("type", ""),
                "material": relic.get("material", ""),
                "imageUrl": img_url,
                "description": relic.get("description", ""),
                "museumId": relic.get("museumId", "")
            })
        except Exception as e:
            print(f"处理失败 {relic.get('objectId')}: {e}")
            failed += 1
            continue

    if not vectors:
        print("无有效特征，索引构建失败")
        return

    vectors_np = np.array(vectors, dtype=np.float32)
    norms = np.linalg.norm(vectors_np, axis=1, keepdims=True)
    vectors_np = np.where(norms > 1e-6, vectors_np / norms, vectors_np)

    index = get_index()
    index.build(vectors_np, metadata_list)
    print(f"索引构建完成！共 {len(vectors)} 条有效特征")

if __name__ == "__main__":
    build_index()