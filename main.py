from fastapi import FastAPI
# 👇 就是这一行漏掉了，必须把它加上 👇
from models.schema import SkillResponse 

app = FastAPI(
    title="SkillCraft AI Backend",
    description="Component casting and open-source hall API for Godot code generation and sandbox testing",
    version="0.1.0",
)

@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to SkillCraft AI Backend"}

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

# === 测试组件拉取接口 ===
@app.get("/api/v1/skills/dummy", response_model=SkillResponse)
async def get_dummy_skill():
    """
    这是一个测试接口，用于返回一个符合“无状态与数据抽离”规范的 Godot 组件。
    前端 (GameCraft) 可以通过解析 export_params 自动生成 UI 滑块。
    """
    return SkillResponse(
        id="skill_001",
        name="Player Movement",
        description="A basic player movement script for 2D games",
        code_content="""extends CharacterBody2D

@export var speed: float = 300.0

func _physics_process(delta):
    var direction = Input.get_vector("ui_left", "ui_right", "ui_up", "ui_down")
    velocity = direction * speed
    move_and_slide()""",
        export_params={"speed": 300.0},
        version="1.0.0",
        author="SkillCraft AI"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)