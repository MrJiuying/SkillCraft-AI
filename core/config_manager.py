import json
import os
from pydantic import BaseModel

CONFIG_FILE = os.path.join(os.getcwd(), "config.json")

class LLMConfig(BaseModel):
    """大模型配置的数据结构"""
    api_key: str = ""
    base_url: str = "https://api.deepseek.com" # 默认指向 DeepSeek
    model_name: str = "deepseek-chat"

def load_config() -> LLMConfig:
    """从本地 JSON 文件读取配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return LLMConfig(**data)
        except Exception:
            pass # 如果读取失败，返回默认配置
    return LLMConfig()

def save_config(config: LLMConfig) -> None:
    """将配置持久化写入本地 JSON 文件"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config.model_dump(), f, indent=4, ensure_ascii=False)