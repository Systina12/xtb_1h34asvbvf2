import streamlit as st
from config.settings import DEFAULT_TARGET_ADAPT, DEFAULT_TARGET_EMPATHY
from models.psychological_stress_model import PsychologicalStressModel


def render_sidebar():
    st.header("🎯 训练配置")
    api_key = st.text_input("请输入你的DeepSeek API Key:", type="password")

    st.markdown("---")
    st.subheader("训练场景选择")
    scenario = st.selectbox(
        "选择训练场景:",
        ["标准场景", "初次诊断告知", "治疗失败应对", "家庭压力管理", "复发情绪危机"]
    )
    st.session_state.training_scenario = scenario

    st.subheader("训练目标设定")
    target_empathy = st.slider("共情准确率目标(%)", 70, 100, st.session_state.targets.get("empathy", DEFAULT_TARGET_EMPATHY))
    target_adaptation = st.slider("策略适配度目标(%)", 70, 100, st.session_state.targets.get("adapt", DEFAULT_TARGET_ADAPT))
    st.session_state.targets = {"empathy": target_empathy, "adapt": target_adaptation}

    st.markdown("---")
    # 实时表现监控（使用 st.session_state.api_evaluation ）
    scores = st.session_state.api_evaluation
    if scores:
        st.subheader("实时表现")
        col1, col2 = st.columns(2)
        with col1:
            delta = scores['empathy_accuracy_rate'] - target_empathy
            color = "normal" if abs(delta) < 5 else ("off" if delta < 0 else "normal")
            st.metric("共情准确率", f"{scores['empathy_accuracy_rate']:.1f}%", delta=f"{delta:+.1f}%", delta_color=color)
        with col2:
            delta = scores['strategy_adaptation_rate'] - target_adaptation
            color = "normal" if abs(delta) < 5 else ("off" if delta < 0 else "normal")
            st.metric("策略适配度", f"{scores['strategy_adaptation_rate']:.1f}%", delta=f"{delta:+.1f}%", delta_color=color)

        status = "🟢" if scores['clinical_standard_met'] else "🔴"
        st.write(f"{status} 临床标准达成: {scores['clinical_standard_met']}")
        if 'analysis' in scores:
            st.caption(f"💡 AI分析: {scores['analysis']}")
        nurse_count = len([h for h in st.session_state.history if h[0] == "护士"])
        st.caption(f"已完成 {nurse_count} 轮对话")
    else:
        st.subheader("实时表现")
        st.info("开始对话后将显示AI实时评估结果")

    if st.button("🔄 重置训练"):
        st.session_state.history = []
        st.session_state.emotions = []
        st.session_state.stress_model = PsychologicalStressModel(st.session_state.stress_model.keyword_rules)
        st.session_state.assessment_history = []
        st.session_state.conversation_round = 0
        st.session_state.api_evaluation = None
        st.session_state.initial_seeded = False  # ⭐ 新增：允许下次输入 Key 后再次自动种子
        st.rerun()

    return api_key