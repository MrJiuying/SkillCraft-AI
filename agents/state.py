from typing import TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    """
    LangGraph 的全局状态字典，用于在各个节点间传递数据。
    """
    user_prompt: str                  # 用户输入的自然语言需求 (如: "写一个基础的移动控制器")
    sop_content: str                  # 从本地读取到的 Godot 组件开发规范 (.md 内容)
    generated_code: Optional[str]     # LLM 生成的原始 GDScript 代码
    parsed_params: Optional[Dict[str, Any]] # 从生成的代码中解析出的 export_params 字典
    error: Optional[str]              # 记录流转过程中的错误信息，供错误处理节点使用