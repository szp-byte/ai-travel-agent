# -*- coding: utf-8 -*-
"""
env_loader.py - 安全地从 .env 读取 API Key

从项目目录的 .env 文件读取 DEEPSEEK_API_KEY 到环境变量。
绝不打印 Key 内容。
"""
import os

def load_dotenv(path=None):
    """读取 .env 文件并设置环境变量(若尚未设置)。返回是否加载到key。"""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key == "DEEPSEEK_API_KEY" and not os.environ.get(key):
                os.environ[key] = value
    return bool(os.environ.get("DEEPSEEK_API_KEY"))

if __name__ == "__main__":
    ok = load_dotenv()
    # 只打印是否成功, 不打印 Key 本身
    print("加载成功" if ok else "未找到 Key")
