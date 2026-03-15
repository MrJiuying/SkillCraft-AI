import os
import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from agents.state import AgentState
from core.config_manager import load_config

class LLMCodeResult(BaseModel):
    skill_name: str = Field(description="组件的英文名称，例如 HealthSystem")
    description: str = Field(description="组件功能的简短描述")
    script_content: str = Field(description="生成的完整 GDScript 源码，必须包含 @export")
    export_params: Dict[str, Any] = Field(description="代码中所有 @export 暴露的参数字典及默认值")

def read_sop_node(state: AgentState) -> dict:
    sop_path = os.path.join(os.getcwd(), "Godot4_Coding_Standard_v1.0.md")
    try:
        with open(sop_path, "r", encoding="utf-8") as f:
            return {"sop_content": f.read()}
    except Exception as e:
        return {"error": f"读取 SOP 失败: {str(e)}"}

def generate_code_node(state: AgentState) -> dict:
    user_prompt = state.get("user_prompt", "")
    sop = state.get("sop_content", "")
    feedback = state.get("feedback") # 获取前一次被打回的报错信息
    
    config = load_config()
    if not config.api_key:
        return {"error": "API Key 未配置。"}

    llm = ChatOpenAI(
        api_key=config.api_key, 
        base_url=config.base_url, 
        model=config.model_name,
        temperature=0.1
    )
    
    parser = JsonOutputParser(pydantic_object=LLMCodeResult)
    
    # 如果有 feedback，说明是被打回重写的，我们要对 AI 更严厉一点
    system_message = "你是一个资深的 Godot 4.x 组件架构师。你必须输出 JSON 格式。\n规范如下：\n{sop}\n\n{format_instructions}"
    if feedback:
        system_message += f"\n\n⚠️ 警告：你上一次生成的代码未通过质检！\n质检报错如下：\n{feedback}\n请仔细修复这些错误并重新生成。"

    prompt_tpl = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "需求：{user_prompt}")
    ]).partial(format_instructions=parser.get_format_instructions())
    
    chain = prompt_tpl | llm | parser
    
    try:
        print(f"🔄 正在生成代码... (第 {state.get('iteration_count', 0) + 1} 次尝试)")
        result = chain.invoke({"sop": sop, "user_prompt": user_prompt})
        return {
            "generated_code": result.get("script_content"),
            "parsed_params": result.get("export_params"),
            "skill_name": result.get("skill_name"),
            "description": result.get("description")
        }
    except Exception as e:
        return {"error": f"LLM 解析 JSON 失败: {str(e)}"}

# 👇 新增：质检节点
def validate_code_node(state: AgentState) -> dict:
    code = state.get("generated_code", "")
    iterations = state.get("iteration_count", 0) + 1
    errors = []

    print("🔍 正在对生成的代码进行质检...")

    # 1. 基础语法强制校验
    if "extends " not in code:
        errors.append("致命错误：缺少 'extends' 关键字，代码必须继承自 Node 或其子类。")
    if "class_name " not in code:
        errors.append("致命错误：缺少 'class_name' 关键字，无法作为独立组件注册。")
    if "@export" not in code and state.get("parsed_params"):
         errors.append("规范错误：JSON 中提取了参数，但代码源码中找不到 '@export' 关键字。")

    # 2. 如果存在错误，打回重写
    if errors:
        error_msg = "\n".join(errors)
        print(f"❌ 质检不通过：\n{error_msg}")
        return {
            "is_valid": False,
            "feedback": "代码质检未通过，请修复以下问题：\n" + error_msg,
            "iteration_count": iterations
        }
    
    print("✅ 质检通过！")
    return {
        "is_valid": True,
        "feedback": None,
        "iteration_count": iterations
    }

# 👇 新增：路由裁决逻辑 (LangGraph 的灵魂)
def route_validation(state: AgentState) -> str:
    """根据质检结果决定下一跳节点"""
    if state.get("error"): # 出现致命错误，直接终止
        return END
    if state.get("is_valid"): # 质检通过，出厂
        return END
    if state.get("iteration_count", 0) >= 3: # 事不过三，防止烧钱死循环
        print("⚠️ 达到最大重试次数 (3次)，强制输出当前结果。")
        return END
    
    # 质检不通过且没达到上限，打回重写节点
    return "generate_code"

# ==========================================
# 3. 重新编译动态图
# ==========================================
def build_agent_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("read_sop", read_sop_node)
    workflow.add_node("generate_code", generate_code_node)
    workflow.add_node("validate_code", validate_code_node) # 加入质检节点
    
    workflow.set_entry_point("read_sop")
    workflow.add_edge("read_sop", "generate_code")
    workflow.add_edge("generate_code", "validate_code") # 生成完毕后交给质检
    
    # 质检完毕后，交给条件路由判定走向
    workflow.add_conditional_edges(
        "validate_code",
        route_validation,
        {
            "generate_code": "generate_code", # 路由返回此字符串，则跳转回生成节点
            END: END                          # 路由返回 END，则结束
        }
    )
    
    return workflow.compile()

class LLMCodeResult(BaseModel):
    skill_name: str = Field(description="组件英文名(必须是大驼峰命名法)，例如：HealthComponent")
    # 👇 新增：强制要求输出中文别名
    alias_zh: str = Field(description="组件的中文具象化别名，例如：生命值核心、弹幕发射器")
    # 👇 新增：强制要求分类
    category: str = Field(description="组件所属的严格分类，必须从以下选项中选择一个：Combat(战斗), Movement(移动), State(状态), System(系统), UI(界面)")
    description: str = Field(description="组件功能的简短描述")
    script_content: str = Field(description="生成的完整 GDScript 源码，必须包含 @export")
    export_params: Dict[str, Any] = Field(description="代码中所有 @export 暴露的参数字典及默认值")

skill_agent_app = build_agent_graph()