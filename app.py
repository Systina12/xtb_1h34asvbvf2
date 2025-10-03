import streamlit as st
from config.settings import APP_TITLE, PAGE_TITLE, LAYOUT
from state.session_state import ensure_state
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.chat import render_history, handle_input

st.set_page_config(page_title=PAGE_TITLE, layout=LAYOUT)
st.title(APP_TITLE)
st.markdown("**角色：** 你是一名护士，正在与不孕症患者小林进行标准化沟通训练。")

# 初始化会话状态
ensure_state()

# 侧边栏 & 获取 API Key
with st.sidebar:
    api_key = render_sidebar()

# 主区域：仪表盘（若已有评估）
if st.session_state.assessment_history:
    render_dashboard()

# 聊天历史 & 输入
render_history()

if api_key:
    handle_input(api_key)
else:
    st.info("👈 请在左侧侧边栏输入您的 DeepSeek API Key 以开始训练。")
    st.markdown(
        """
        ### 🎯 训练目标
        - **共情响应准确率** ≥ 85%
        - **情绪疏导策略适配度** ≥ 90%
        - **基于SCL-90/HADS量表的心理评估能力**

        ### 📚 训练场景
        1. **标准场景** - 基础沟通训练
        2. **初次诊断告知** - 坏消息告知技巧
        3. **治疗失败应对** - 挫折情绪管理
        4. **家庭压力管理** - 家庭系统干预
        5. **复发情绪危机** - 危机干预技能
        """
    )