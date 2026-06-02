# backend/models.py
from pydantic import BaseModel, Field
from typing import Optional, List

# ---------- 后端 API 返回的文物结构（对应 GET /api/v1/data/relics 的 records 项） ----------
class RelicRecord(BaseModel):
    objectId: str
    title: str
    period: Optional[str] = ""
    type: Optional[str] = ""
    material: Optional[str] = ""
    description: Optional[str] = ""
    dimensions: Optional[str] = ""
    museumId: Optional[str] = ""
    detailUrl: Optional[str] = ""
    imageUrl: Optional[str] = ""
    imagePath: Optional[str] = ""
    creditLine: Optional[str] = ""
    accessionNumber: Optional[str] = ""
    crawlDate: Optional[str] = ""
    createTime: Optional[str] = ""
    updateTime: Optional[str] = ""
    isDeleted: Optional[int] = 0
    popularity: Optional[int] = 0

# ---------- 分页响应包装 ----------
class RelicListData(BaseModel):
    records: List[RelicRecord]
    total: int
    page: int
    pageSize: int

class ApiResponse(BaseModel):
    code: int
    message: str
    data: RelicListData

# ---------- 以图搜图请求/响应 ----------
class SearchResultItem(BaseModel):
    objectId: str
    title: str
    period: str
    type: str
    material: str
    imageUrl: str
    similarity: float   # 余弦相似度，0~1

class SearchResponseData(BaseModel):
    results: List[SearchResultItem]

class SearchResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: SearchResponseData

# ---------- 内部使用的文物元数据（带特征向量，可选） ----------
class RelicMetadata(BaseModel):
    objectId: str
    title: str
    period: str
    type: str
    material: str
    imageUrl: str
    description: str = ""
    museumId: str = ""