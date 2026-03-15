# 🧱 SkillCraft AI

> **Godot 4.x 工业级组件自动化铸造与资产管理中心**

SkillCraft AI 是一个基于大语言模型（LLM）和 Agentic Workflow（智能体工作流）的后端引擎。它能够将自然语言需求，转化为严格遵守 Godot 4.x 最佳实践的解耦组件（GDScript），并提供带版本控制的本地资产库和可视化监控大屏。

---

## ✨ 核心功能 (Features)

1. **🧠 AI 智能铸造 (Agentic Generation)**
   - 基于 `LangGraph` 构建的循环工作流。
   - 严格遵循内置的《Godot 4.x 组件设计宪法》(SOP)，强制产出数据与逻辑分离、基于 `@export` 和事件总线 (EventBus) 的高质量代码。
2. **🛡️ 自动质检与纠错 (Self-Reflection)**
   - 内置代码质检节点（Linter Node）。
   - 自动拦截缺少 `class_name`、`extends` 等关键语法的“劣质砖块”，并带上报错信息打回重写，拒绝死循环，事不过三。
3. **📦 本地资产库 (Asset Library)**
   - 内置 `SQLite` 数据库。
   - 支持将满意的组件一键入库，支持中文别名、按功能分类（如 Combat, Movement, State 等）管理，支持一键删除。
   - 预留 `cloud_id` 和 `is_synced` 字段，为未来的云端集市平滑过渡。
4. **📺 开发者监控大屏 (Dashboard)**
   - 基于 `Streamlit` 构建的轻量级前端。
   - 提供 API Key 配置、实时 Prompt 测试、代码高亮预览、UI 契约 (JSON) 提取以及仓库资产树状管理。

---

## 🏗️ 系统架构 (Architecture)

系统分为三个核心层级：

- **网关层 (API Gateway)**: 基于 `FastAPI`，提供 RESTful 接口（`/api/v1/...`），负责前后端数据交互。
- **智能体层 (Agent Layer)**: 基于 `LangGraph` + `DeepSeek`，包含读取规范、生成代码、语法校验、条件路由判定四个节点。
- **数据层 (Data Layer)**: 基于 `SQLAlchemy` + `SQLite`，实现 JSON 契约与 GDScript 源码的持久化存储。

### 📁 核心目录结构

```text
SkillCraft-AI/
├── agents/                  # AI 智能体大脑
│   ├── state.py             # LangGraph 状态字典定义 (记录重试次数、报错反馈等)
│   └── workflow.py          # 核心工作流引擎 (生成 -> 质检 -> 路由循环)
├── core/                    # 核心配置
│   └── config_manager.py    # 动态读取/保存 LLM 配置 (防泄露设计)
├── models/                  # 数据契约与模型
│   ├── database.py          # SQLite 数据库与 ORM 模型 (SkillRecord)
│   └── schema.py            # FastAPI 请求/响应的 Pydantic 数据校验
├── ui/                      # 监控大屏
│   └── dashboard.py         # Streamlit 可视化界面
├── Godot4_Coding_Standard_v1.0.md # 🔴 系统最高宪法 (Godot 4.x 开发规范)
└── main.py                  # FastAPI 主入口与路由控制器