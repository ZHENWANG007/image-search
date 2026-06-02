from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import numpy as np
from typing import List, Dict

from config import DEFAULT_TOP_K, DEFAULT_THRESHOLD
from feature_extractor import get_extractor
from faiss_index import get_index

from models import SearchResponse, SearchResponseData, SearchResultItem
app = FastAPI(title="Museum Image Search API")

# 启动时加载索引
@app.on_event("startup")
async def load_index():
    index = get_index()
    if not index.load():
        print("警告: FAISS 索引文件不存在，请先运行 init_index.py 构建索引")
    else:
        print(f"索引加载成功，共 {len(index.metadata)} 条文物")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/v1/search/image")
async def search_by_image(
    file: UploadFile = File(...),
    top_k: int = DEFAULT_TOP_K,
    threshold: float = DEFAULT_THRESHOLD
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "文件必须是图片")
    
    try:
        img_bytes = await file.read()
        if len(img_bytes) == 0:
            raise HTTPException(400, "空文件")
        
        extractor = get_extractor()
        query_vec = extractor.extract(img_bytes)
        
        index = get_index()
        if index.index is None:
            raise HTTPException(503, "索引未加载")
        
        results = index.search(query_vec, k=top_k)

        # ====================== 修复 1：过滤条件写反 ======================
        filtered = [(dist, meta) for dist, meta in results if dist >= threshold]
        # =================================================================

        # 打印调试（必开，看为什么空）
        print("原始检索结果（相似度）：", [d for d, m in results])
        print("过滤后剩余：", len(filtered))

        response_data = SearchResponseData(results=[
            SearchResultItem(
                objectId=meta["objectId"],
                title=meta["title"],
                period=meta.get("period", ""),
                type=meta.get("type", ""),
                material=meta.get("material", ""),
                imageUrl=meta["imageUrl"],
                similarity=dist  # ====================== 修复 2：变量名 ======================
            ) for dist, meta in filtered
        ])
        return SearchResponse(code=200, message="success", data=response_data)

    except HTTPException:
        raise
    except Exception as e:
        print("搜索错误：", e)
        raise HTTPException(500, f"内部错误: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)