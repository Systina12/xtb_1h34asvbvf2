import streamlit as st
import pandas as pd
import plotly.express as px
from config.settings import STRESS_HIGH_RISK


def render_dashboard():
    if not st.session_state.assessment_history:
        return
    st.header("📊 专业评估仪表板")
    tab1, tab2, tab3 = st.tabs(["情绪轨迹分析", "能力评估", "训练报告"])

    with tab1:
        df = pd.DataFrame([{
            'round': a['round'],
            '焦虑': a['emotions'].get('anxiety', 0) * 10,
            '悲伤': a['emotions'].get('sadness', 0) * 10,
            '希望': a['emotions'].get('hope', 0) * 10,
            '压力水平': a['stress_level']
        } for a in st.session_state.assessment_history])
        if not df.empty:
            fig = px.line(df, x='round', y=['焦虑', '悲伤', '希望', '压力水平'], title="患者情绪轨迹与压力水平")
            fig.add_hline(y=STRESS_HIGH_RISK, line_dash="dash", line_color="red", annotation_text="高风险阈值")
            st.plotly_chart(fig, use_container_width=True)
        if st.session_state.stress_model.intervention_triggers:
            st.subheader("干预触发记录")
            for t in st.session_state.stress_model.intervention_triggers:
                st.warning(f"第{t['round']}轮: {t['type']} (压力水平: {t['stress_levels']})")

    with tab2:
        scores = st.session_state.api_evaluation
        if scores and scores.get('overall_competency', 0) > 0:
            categories = ['共情准确率', '策略适配度', '压力管理', '沟通效果']
            values = [
                scores['empathy_accuracy_rate'] / 100 * 5,
                scores['strategy_adaptation_rate'] / 100 * 5,
                min(5, (100 - max(0, scores['empathy_accuracy_rate'] - 85)) / 20 * 5),
                scores['overall_competency'] / 100 * 5
            ]
            df_radar = pd.DataFrame({'category': categories + [categories[0]], 'value': values + [values[0]]})
            fig_radar = px.line_polar(df_radar, r='value', theta='category', line_close=True, title="护理能力评估雷达图(AI评估)")
            st.plotly_chart(fig_radar, use_container_width=True)
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("综合能力分数", f"{scores['overall_competency']:.1f}/100")
            with col2: st.metric("共情准确率", f"{scores['empathy_accuracy_rate']:.1f}%")
            with col3: st.metric("策略适配度", f"{scores['strategy_adaptation_rate']:.1f}%")
        else:
            st.info("进行对话后将显示AI能力评估结果")

    with tab3:
        scores = st.session_state.api_evaluation
        if scores and scores.get('overall_competency', 0) > 0:
            st.subheader("训练绩效报告(AI评估)")
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**会话轮数:** {len([h for h in st.session_state.history if h[0] == '护士'])}")
                st.info(f"**训练场景:** {st.session_state.training_scenario}")
            with col2:
                status = "✅ 达标" if scores['clinical_standard_met'] else "❌ 未达标"
                st.success(f"**临床标准:** {status}")
                st.success(f"**综合评分:** {scores['overall_competency']:.1f}/100")
            if 'analysis' in scores:
                st.subheader("AI专家分析")
                st.write(scores['analysis'])
            st.subheader("AI推荐改进方案")
            if scores['empathy_accuracy_rate'] < 85:
                st.write("🔹 **共情能力需提升**: 建议增加情感识别和反映训练")
            if scores['strategy_adaptation_rate'] < 90:
                st.write("🔹 **策略适配需优化**: 建议学习情境化沟通技巧")
            if scores['clinical_standard_met']:
                st.success("🎉 所有AI评估指标均已达到临床标准！")
        else:
            st.info("进行对话后将显示AI训练报告")