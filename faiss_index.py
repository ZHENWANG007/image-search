import faiss
import numpy as np
import json
from typing import List, Tuple, Dict, Any
from config import INDEX_PATH, METADATA_PATH, FEATURE_DIM

class FaissIndex:
    def __init__(self, dimension: int = FEATURE_DIM):
        self.dimension = dimension
        self.index = None
        self.metadata: List[Dict[str, Any]] = []   # 每个元素对应一个文物的元信息
    
    def build(self, vectors: np.ndarray, metadata_list: List[Dict]):
        """
        vectors: shape (N, dimension), dtype float32, 已归一化
        metadata_list: 长度 N 的列表，元素字典（至少包含 objectId, title, imageUrl 等）
        """
        assert vectors.shape[1] == self.dimension
        assert vectors.shape[0] == len(metadata_list)
        # 创建内积索引（余弦相似度）
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)
        self.metadata = metadata_list
        # 保存到磁盘
        self.save()
    
    def search(self, query_vec: np.ndarray, k: int = 5) -> List[Tuple[float, Dict]]:
        """
        检索最相似的 k 个文物
        返回 [(similarity, metadata), ...] 按相似度降序
        """
        if self.index is None:
            raise RuntimeError("Index not built or loaded.")
        query_vec = query_vec.reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(query_vec, k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            results.append((float(dist), self.metadata[idx]))
        return results
    
 
    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, INDEX_PATH)
            with open(METADATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def load(self):
        import os
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            return True
        return False

# 全局单例
_index = FaissIndex()
def get_index():
    global _index
    return _index