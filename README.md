# 文物以图搜图检索
## 简介
基于**ResNet50图像特征提取 + FAISS向量相似度检索 + SQLite存储**实现的文物以图搜图后端服务，通过上传文物图片，提取图像特征后在文物库中匹配余弦相似度最高的同类文物，提供FastAPI接口对外调用。

## 技术栈
- 后端框架：FastAPI
- 特征提取：Pytorch + ResNet50
- 向量检索：faiss-cpu（余弦相似度，IndexFlatIP）
- 数据存储：SQLite（文物基础信息）、本地文件（faiss索引+元数据json）
- 网络请求：requests

## 目录结构
```
backend/
├── config.py          # 全局配置、接口地址、参数、路径定义
├── database.py        # SQLite数据库初始化、增查操作
├── faiss_index.py     # FAISS索引构建、存储、加载、向量检索
├── feature_extractor.py # ResNet50图像特征提取器（单例）
├── init_index.py      # 全量拉取文物数据、下载图片、构建向量索引入口
├── main.py            # FastAPI服务主文件，检索接口
├── models.py          # Pydantic接口返回数据模型定义
├── requirements.txt   # 项目依赖
└── data/              # 自动生成：sqlite库、faiss索引、metadata.json
```

## 环境部署
### 1. 安装依赖
```bash
pip install -r requirements.txt
```
> 注意：faiss-cpu根据自身环境安装，GPU环境可替换为faiss-gpu；torch如需CUDA自行匹配cuda版本。

### 2. 配置说明
`config.py`中关键配置项：
1. `RELIC_API_BASE`：文物数据源API地址
2. `ACCESS_TOKEN/HEADERS`：接口鉴权信息
3. `DEFAULT_THRESHOLD`：相似度筛选阈值（默认0.4，大于等于阈值才返回结果）
4. `DEFAULT_TOP_K`：默认检索返回条数
5. `DEVICE`：`cpu/cuda`，显卡可用改为`cuda`加速特征提取

## 使用步骤
### 步骤1：初始化数据库&构建FAISS向量索引
首次启动必须执行，拉取远程文物数据→入库→下载文物图片→提取特征→生成faiss索引文件
```bash
python init_index.py
```
- 执行完毕自动在`data/`生成：`relics.db`、`relic_index.faiss`、`relic_metadata.json`

### 步骤2：启动API检索服务
```bash
python main.py
```
服务默认地址：`http://0.0.0.0:8000`
接口文档地址：
- Swagger：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

## 接口说明
### 1. 健康检查
`GET /health`
```json
{"status":"ok"}
```

### 2. 图片检索接口（核心）
`POST /api/v1/search/image`
- 请求参数：
  - `file`: 上传图片文件（必填）
  - `top_k`: 自定义返回数量，默认20
  - `threshold`: 自定义相似度阈值，默认0.4
- 返回示例：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "results": [
      {
        "objectId": "xxx",
        "title": "文物名称",
        "period": "朝代",
        "type": "器型",
        "material": "材质",
        "imageUrl": "原图链接",
        "similarity": 0.852
      }
    ]
  }
}
```
> similarity：余弦相似度[0~1]，数值越高图片越相似

## 关键参数调整
1. **相似度阈值**：`config.py DEFAULT_THRESHOLD`，数值越小匹配结果越多，越大匹配越精准
2. **返回条数**：`DEFAULT_TOP_K`调整默认返回候选数量
3. **特征尺寸**：`IMAGE_MAX_SIZE`修改ResNet输入图片尺寸
4. **拉取数据量**：`init_index.py`中`if len(relics) >=100`可修改上限，拉取更多文物构建索引

## 常见问题
1. **启动提示索引不存在**：未执行`init_index.py`生成索引文件，先构建索引再启动服务
2. **检索无返回数据**：
   - 图片特征与库中文物相似度低于阈值，调低`DEFAULT_THRESHOLD`
   - 构建索引时大量图片下载失败，检查文物图片url有效性
3. **GPU加速**：修改`config.py DEVICE="cuda"`，保证torch、cuda环境正常
4. **接口鉴权失效**：更新`ACCESS_TOKEN`令牌

## 数据文件说明
`data`文件夹由程序自动创建：
- `relics.db`：SQLite库，存储全量文物结构化信息
- `relic_index.faiss`：FAISS向量索引文件
- `relic_metadata.json`：索引与文物id映射元数据
