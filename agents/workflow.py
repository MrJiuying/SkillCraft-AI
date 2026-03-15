import os
from langgraph.graph import StateGraph, END
from agents.state import AgentState
from core.config_manager import load_config


def read_sop_node(state: AgentState) -> dict:
    """
    节点：读取本地的 Godot 开发规范 SOP。
    这是强制的前置步骤，确保大模型拥有绝对的物理隔离与无状态开发意识。
    
    Args:
        state (AgentState): 当前图状态
        
    Returns:
        dict: 包含 sop_content 的状态更新字典
    """
    # 假设规范文件在项目根目录
    sop_path = os.path.join(os.getcwd(), "Godot4_Coding_Standard_v1.0.md")
    
    try:
        with open(sop_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"sop_content": content}
    except Exception as e:
        # FIXME: 生产环境中应该有更好的 fallback 机制，而不是直接抛出错误文本
        return {"error": f"读取 SOP 失败: {str(e)}"}

def generate_code_node(state: AgentState) -> dict:
    """
    节点：调用 LLM，根据用户需求和 SOP 生成 Godot 组件代码。
    
    Args:
        state (AgentState): 当前图状态
        
    Returns:
        dict: 包含 generated_code 和 parsed_params 的状态更新字典
    """
    prompt = state.get("user_prompt", "")
    sop = state.get("sop_content", "")
    
    # TODO: 这里需要真正接入大模型 (LLM) 进行推理
    # 目前先用 Mock 数据占位，跑通流程
    
    mock_gdscript = """extends Node\n\n@export var test_speed: float = 300.0\n\n# 这是一个占位生成的代码"""
    mock_params = {"test_speed": 300.0}
    
    return {
        "generated_code": mock_gdscript,
        "parsed_params": mock_params
    }

def build_agent_graph():
    """
    构建并编译 LangGraph 状态图。
    流转顺序: START -> read_sop_node -> generate_code_node -> END
    """
    # 初始化状态图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("read_sop", read_sop_node)
    workflow.add_node("generate_code", generate_code_node)
    
    # 定义边 (流转逻辑)
    workflow.set_entry_point("read_sop")
    workflow.add_edge("read_sop", "generate_code")
    workflow.add_edge("generate_code", END)
    
    # 编译成可执行的图
    return workflow.compile()

def generate_code_node(state: AgentState) -> dict:
    """节点：调用第三方大模型 API 生成结构化代码"""
    user_prompt = state.get("user_prompt", "")
    sop = state.get("sop_content", "")
    
    # 👇 动态读取持久化配置
    config = load_config()
    
    # 拦截校验：如果没有配置 API Key，直接熔断报错，不发起请求
    if not config.api_key:
        return {"error": "API Key 未配置，请先调用 /api/v1/config 接口保存您的 API Key。"}
    
    # 初始化大模型 (使用动态读取的配置)
    llm = ChatOpenAI(
        api_key=config.api_key, 
        base_url=config.base_url, 
        model=config.model_name,
        temperature=0.1, 
        max_retries=3
    )
    
    # 核心魔法：将 LLM 绑定到我们的 Pydantic 模型上
    structured_llm = llm.with_structured_output(LLMCodeResult)
    
    # 构建系统提示词与人类需求
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个资深的 Godot 4.x 组件架构师。\n你必须严格遵守以下开发规范来编写代码：\n\n{sop}"),
        ("human", "请根据我的需求生成组件代码，并提取 export_params。\n用户需求：{user_prompt}")
    ])
    
    # 组装管道并触发调用
    chain = prompt | structured_llm
    
    try:
        result: LLMCodeResult = chain.invoke({"sop": sop, "user_prompt": user_prompt})
        
        return {
            "generated_code": result.script_content,
            "parsed_params": result.export_params,
            "skill_name": result.skill_name,
            "description": result.description
        }
    except Exception as e:
        return {"error": f"LLM 生成代码失败: {str(e)}"}

# 导出一个编译好的图实例供 main.py 调用
skill_agent_app = build_agent_graph()