# 新建 test_feature.py
import requests
from feature_extractor import get_extractor
from config import HEADERS

# 测试同一张图片的特征是否一致
extractor = get_extractor()
# 取一个已知的文物图片URL
img_url = "你的文物图片URL"
resp = requests.get(img_url, headers=HEADERS)
img_bytes = resp.content

# 两次提取特征
vec1 = extractor.extract(img_bytes)
vec2 = extractor.extract(img_bytes)

# 计算余弦相似度（应接近1）
sim = np.dot(vec1, vec2)
print(f"同图特征相似度: {sim}")  # 正常应≥0.99