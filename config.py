import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 文物接口地址
RELIC_API_BASE = "http://60.205.14.101:8080/api/v1/data/relics"

# 索引文件路径
INDEX_PATH = os.path.join(DATA_DIR, "relic_index.faiss")
METADATA_PATH = os.path.join(DATA_DIR, "relic_metadata.json")

# 检索配置
DEFAULT_TOP_K = 20
DEFAULT_THRESHOLD = 0.4   # 余弦相似度阈值

# 图片下载配置
IMAGE_DOWNLOAD_TIMEOUT = 10  # 秒
IMAGE_MAX_SIZE = (224, 224)  # ResNet 输入尺寸

# 特征提取配置
FEATURE_DIM = 2048            # 最终特征维度
DEVICE = "cpu"               # 可改为 "cuda"
# 分页大小
PAGE_SIZE = 10
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJkNDIwNzdiNi1iZjI5LTRlMzgtYWY4OS1mZmZlNjgyMDk1NTIiLCJ1c2VyVHlwZSI6IkFETUlOIiwiaWF0IjoxNzgwMzkxMDAwLCJleHAiOjE3ODAzOTgyMDB9.kSY8umwJ7oKUyj-aSw90WF4HWNdCwtQ87E-YDe_8Apk"
HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}