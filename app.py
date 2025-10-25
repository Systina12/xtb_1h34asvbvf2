# -*- coding: utf-8 -*-
import streamlit as st
from config.settings import APP_TITLE, PAGE_TITLE, LAYOUT
from state.session_state import ensure_state
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.chat import render_history, handle_input
from components.video_emotion_app import render_video_emotion_page   # 导入新的视频模块

st.set_page_config(page_title=PAGE_TITLE, layout=LAYOUT)
st.title(APP_TITLE)

# 初始化会话状态
ensure_state()

# 侧边栏 & 获取 API Key
with st.sidebar:
    api_key = render_sidebar()

# 顶部 Tab：沟通训练 / 视频情绪识别
tab1, tab2 = st.tabs(["🩺 沟通训练", "🎬 视频情绪识别"])

with tab1:
    st.markdown("**角色：** 你是一名护士，正在与不孕症患者小林进行标准化沟通训练。")

    # —— 开局种子：仅当已输入 API Key 且历史为空且未种子时执行一次 ——
    if api_key and not st.session_state.get("initial_seeded", False) and not st.session_state.history:


        # 2) 初始情绪（可按需调整）
        base_emotion = {"anxiety": 0.85, "sadness": 0.80, "hope": 0.15}

        # 3) 关键词二次修正 + 裁剪到 [0,1]
        adjusted = {
            "anxiety": max(0.0, min(1.0, base_emotion["anxiety"] )),
            "sadness": max(0.0, min(1.0, base_emotion["sadness"])),
            "hope":    max(0.0, min(1.0, base_emotion["hope"])),
        }

        # 4) 评估一次（round=0），让仪表盘立即可用
        assessment = st.session_state.stress_model.assess_emotion_pattern(adjusted, conversation_round=0)
        st.session_state.assessment_history.append(assessment)
        st.session_state.emotions.append(adjusted)

        # 5) 只种子一次
        st.session_state.initial_seeded = True

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

with tab2:
    render_video_emotion_page()
