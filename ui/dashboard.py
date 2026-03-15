import streamlit as st
import requests

st.set_page_config(page_title="SkillCraft AI - 铸造厂监控台", layout="wide")

API_BASE = "http://127.0.0.1:8000/api/v1"

# --- 初始化配置 ---
def get_current_config():
    try:
        res = requests.get(f"{API_BASE}/config")
        if res.status_code == 200:
            return res.json()
    except:
        return None
    return None

initial_config = get_current_config() or {"api_key": "", "base_url": "https://api.deepseek.com"}

# ==========================================
# 侧边栏：配置中心 & 本地资产库
# ==========================================
with st.sidebar:
    st.title("🧱 SkillCraft 控制台")
    
    # 1. 配置区 (做成折叠面板，节省空间)
    with st.expander("⚙️ 系统与模型配置", expanded=False):
        api_key = st.text_input("API Key", value=initial_config.get("api_key", ""), type="password")
        base_url = st.text_input("Base URL", value=initial_config.get("base_url", ""))
        if st.button("保存配置"):
            requests.post(f"{API_BASE}/config", json={
                "api_key": api_key, "base_url": base_url, "model_name": "deepseek-chat"
            })
            st.success("已持久化！")
            
    st.divider()

    # 2. 资产库展示区 (Data Layer UI)
    st.header("📚 我的资产库")
    colA, colB = st.columns([1, 1])
    with colB:
        if st.button("🔄 刷新仓库"):
            st.rerun() # 刷新当前页面读取最新数据库
            
    try:
        lib_res = requests.get(f"{API_BASE}/library/skills")
        if lib_res.status_code == 200:
            skills = lib_res.json()
            if not skills:
                st.info("📦 仓库空空如也，快去生成第一块砖吧！")
            else:
                # 按 Category (分类) 对组件进行分组展示
                categories = set([s.get("category", "未分类") for s in skills])
                for cat in sorted(categories):
                    with st.expander(f"📁 {cat} ({len([s for s in skills if s.get('category') == cat])})"):
                        for s in skills:
                            if s.get("category") == cat:
                                # 使用列布局把名字和删除按钮放在同一行
                                col_name, col_action = st.columns([4, 1])
                                with col_name:
                                    sync_icon = "☁️" if s.get("cloud_synced") else "💻"
                                    st.markdown(f"**{s.get('alias_zh', s.get('name'))}** {sync_icon}")
                                    st.caption(f"`{s.get('name')}`")
                                with col_action:
                                    # Streamlit 循环里的按钮必须有独一无二的 key
                                    if st.button("🗑️", key=f"del_{s.get('id')}", help="删除此组件"):
                                        requests.delete(f"{API_BASE}/library/skills/{s.get('id')}")
                                        st.toast(f"已删除 {s.get('alias_zh')}")
                                        st.rerun() # 刷新界面
        else:
            st.error("无法读取资产库。")
    except Exception as e:
        st.warning("等待后端服务连接...")

# ==========================================
# 主界面：AI 生成车间
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 需求输入")
    prompt = st.text_area("想要生成什么类型的 Godot 组件？", placeholder="例如：写一个 2D 俯视角射击的弹幕发射器，包含射速、散射角度等参数...")
    
    if st.button("🚀 开始铸造 (调用 LangGraph)", use_container_width=True):
        with st.spinner("🧠 AI 正在根据'宪法'架构代码，并进行质检..."):
            try:
                res = requests.post(f"{API_BASE}/skills/generate?prompt={prompt}")
                if res.status_code == 200:
                    st.session_state.last_result = res.json()
                    st.success("生成并通过质检！")
                else:
                    st.error(f"生成失败: {res.json().get('detail', res.text)}")
            except Exception as e:
                st.error(f"网络请求失败: {e}")

with col2:
    st.header("📦 质检与交付成果")
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        
        # --- 资产入库编辑表单 ---
        st.subheader("⚙️ 资产入库配置")
        
        # 允许用户在入库前手动修改 AI 生成的名字
        edit_alias = st.text_input("中文别名", value=result.get('alias_zh', result.get('name', '未命名')))
        
       # 定义友好的分类字典与辅助说明
        category_help = """
        **📘 SkillCraft 组件分类指南：**
        * ⚔️ **Combat (战斗)**：处理生命值、伤害计算、武器发射、弹幕、无敌帧等。
        * 🏃‍♂️ **Movement (移动)**：处理玩家控制、跳跃重力、冲刺、怪物寻路等。
        * 📊 **State (数据/状态)**：处理金币收集、背包物品、经验升级、Buff/Debuff等纯数据逻辑。
        * ⚙️ **System (系统)**：处理回合控制、敌人生成器、事件总线、存档读取等全局控制。
        * 🖥️ **UI (界面)**：处理血条更新、弹窗动画、金币数量显示等纯视觉逻辑。
        * 🧩 **Other (其他)**：暂无法归类的杂项组件。
        """
        
        cat_options = ["Combat", "Movement", "State", "System", "UI", "Other"]
        default_cat = result.get('category', 'System')
        if default_cat not in cat_options:
            default_cat = "System"
            
        edit_category = st.selectbox(
            "分类目录", 
            options=cat_options, 
            index=cat_options.index(default_cat),
            help=category_help  # 👈 核心：加入这行，Streamlit 会自动生成一个问号图标
        )

        st.info(f"**组件功能**: {result.get('description')}")
        
        # 👇 入库按钮使用用户修改后的值 👇
        if st.button("💾 将此组件存入我的资产库", type="primary", use_container_width=True):
            save_payload = {
                "name": result.get("name"),
                "alias_zh": edit_alias,          # 使用上面输入框里的最新值
                "category": edit_category,       # 使用上面下拉菜单里的最新值
                "description": result.get("description"),
                "code_content": result.get("code_content"),
                "export_params": result.get("export_params")
            }
            save_res = requests.post(f"{API_BASE}/library/skills", json=save_payload)
            if save_res.status_code == 200:
                st.toast("✅ 成功存入本地数据库！请点击左侧'刷新仓库'查看。")
            else:
                st.error("入库失败！")
        
        # 展示 UI 参数字典
        st.subheader("暴露给前端的 UI 契约 (JSON)")
        st.json(result.get('export_params', {}))
        
        # 展示最终代码
        st.subheader(f"Godot 源码 ({result.get('name')}.gd)")
        st.code(result.get('code_content', ''), language="gdscript")