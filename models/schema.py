from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class SkillResponse(BaseModel):
    id: str = Field(..., description="Unique identifier for the skill")
    name: str = Field(..., description="Name of the Godot component skill")
    description: str = Field(..., description="Detailed description of the skill")
    code_content: str = Field(..., description="Generated Godot script code")
    
    # 【核心补充】：暴露给前端 (GameCraft) 的参数字典，用于生成 UI 面板
    export_params: Dict[str, Any] = Field(default_factory=dict, description="Exposed @export variables for GameCraft configuration")
    
    version: str = Field(default="1.0.0", description="Version of the skill")
    author: Optional[str] = Field(default=None, description="Author of the skill")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "skill_001",
                "name": "Player Movement",
                "description": "A basic player movement script for 2D games",
                # 注意这里的 @export
                "code_content": "extends CharacterBody2D\n\n@export var speed: float = 300.0\n\nfunc _physics_process(delta):\n    var direction = Input.get_vector(\"ui_left\", \"ui_right\", \"ui_up\", \"ui_down\")\n    velocity = direction * speed\n    move_and_slide()",
                # 前端读取这个字典，就知道 UI 上需要渲染一个叫 speed 的数字输入框，默认值是 300.0
                "export_params": {
                    "speed": 300.0
                },
                "version": "1.0.0",
                "author": "SkillCraft AI",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }