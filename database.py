# backend/database.py
import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from config import DATA_DIR
import os

DB_PATH = os.path.join(DATA_DIR, "relics.db")

# ---------- 数据库表结构 ----------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS relics (
    objectId TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    period TEXT,
    type TEXT,
    material TEXT,
    imageUrl TEXT,
    description TEXT,
    museumId TEXT,
    popularity INTEGER,
    createTime TEXT,
    updateTime TEXT
);
CREATE INDEX IF NOT EXISTS idx_title ON relics(title);
CREATE INDEX IF NOT EXISTS idx_period ON relics(period);
"""

@contextmanager
def get_db_connection():
    """获取数据库连接（上下文管理器）"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使返回结果为字典样式
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_database():
    """初始化数据库表（首次运行）"""
    with get_db_connection() as conn:
        conn.executescript(CREATE_TABLE_SQL)

def insert_relic(relic: Dict[str, Any]):
    """插入或替换一条文物记录"""
    with get_db_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO relics 
            (objectId, title, period, type, material, imageUrl, description, museumId, popularity, createTime, updateTime)
            VALUES (:objectId, :title, :period, :type, :material, :imageUrl, :description, :museumId, IFNULL(:popularity,0), :createTime, :updateTime)
        """, relic)

def insert_many_relics(relics: List[Dict[str, Any]]):
    """批量插入文物记录"""
    with get_db_connection() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO relics 
            (objectId, title, period, type, material, imageUrl, description, museumId, popularity, createTime, updateTime)
            VALUES (:objectId, :title, :period, :type, :material, :imageUrl, :description, :museumId, IFNULL(:popularity,0), :createTime, :updateTime)
        """, relics)

def get_all_relics() -> List[Dict[str, Any]]:
    """获取所有文物（用于构建索引）"""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM relics")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def get_relic_by_id(objectId: str) -> Optional[Dict[str, Any]]:
    """根据 objectId 获取单个文物"""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM relics WHERE objectId = ?", (objectId,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_all_relics():
    """清空表（用于重建）"""
    with get_db_connection() as conn:
        conn.execute("DELETE FROM relics")