import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import numpy as np
import io
from config import DEVICE, IMAGE_MAX_SIZE

class FeatureExtractor:
    def __init__(self):
        self.device = torch.device(DEVICE)
        # 加载预训练 ResNet50，去掉最后的分类层（fc）
        backbone = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        # 移除全连接层，保留到平均池化层输出（2048 维）
        self.model = torch.nn.Sequential(*list(backbone.children())[:-1])
        self.model.to(self.device)
        self.model.eval()

        self.transform = transforms.Compose([
            transforms.Resize(IMAGE_MAX_SIZE, antialias=True),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def extract(self, image_bytes: bytes) -> np.ndarray:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                # 输出形状: (1, 2048, 1, 1) -> 压缩为 (1, 2048)
                feat = self.model(tensor).squeeze().cpu().numpy()
            # L2 归一化
            norm = np.linalg.norm(feat)
            if norm < 1e-6:
                feat = np.zeros_like(feat)
            else:
                feat = feat / norm
            return feat.astype("float32")
        except Exception as e:
            raise RuntimeError(f"图片损坏/无法提取特征: {e}")

# 全局单例
_extractor = None
def get_extractor():
    global _extractor
    if _extractor is None:
        _extractor = FeatureExtractor()
    return _extractor