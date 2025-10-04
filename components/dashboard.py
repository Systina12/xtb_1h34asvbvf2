# components/dashboard.py
# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from config.settings import STRESS_HIGH_RISK

# 是否让图表固定在顶部（你可以改成 False）
STICKY_ENABLED = True
STICKY_CLASS = "emotion-sticky-card"

def _inject_sticky_css_once():
    if not STICKY_ENABLED:
        return
    # 只注入一次 CSS
    if not st.session_state.get("_sticky_css_injected", False):
        st.markdown(
            f"""
            <style>
            .{STICKY_CLASS} {{
                position: sticky;
                top: 0;                 /* 与页面顶端的距离，可按需调整 */
                z-index: 999;
                background: var(--background-color,#ffffff);
                padding-top: 0.25rem;
                padding-bottom: 0.25rem;
                border-bottom: 1px solid rgba(0,0,0,0.05);
            }}
            /* 避免 sticky 区域左右被内容挤压 */
            section.main .block-container {{
                padding-top: 0.5rem;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        st.session_state["_sticky_css_injected"] = True


def render_dashboard():
    if not st.session_state.assessment_history:
        return


    tab1, tab2, tab3 = st.tabs(["情绪轨迹分析", "能力评估", "训练报告"])

    with tab1:
        # 构建数据帧
        df = pd.DataFrame([{
            'round': a['round'],
            '焦虑': a['emotions'].get('anxiety', 0) * 10,
            '悲伤': a['emotions'].get('sadness', 0) * 10,
            '希望': a['emotions'].get('hope', 0) * 10,
            '压力水平': a['stress_level']
        } for a in st.session_state.assessment_history]).sort_values("round")

        if not df.empty:
            # —— 分组柱状图的数据准备 ——
            m = df.melt(
                id_vars='round',
                value_vars=['焦虑', '悲伤', '希望', '压力水平'],
                var_name='variable',
                value_name='value'
            ).sort_values(["variable", "round"])

            # 计算每个指标逐轮的变化量（与上一轮相比）
            m["delta"] = m.groupby("variable")["value"].diff().fillna(0.0)

            # 生成用于显示的标签文本：加粗、换行、带Δ
            # 例如： <b>焦虑 7.5<br>Δ +0.5</b>
            m["label"] = m.apply(
                lambda r: f"<b>{r['variable']} {r['value']:.1f}<br>Δ {r['delta']:+.1f}</b>",
                axis=1
            )

            # —— 画分组柱状图 ——
            fig = px.bar(
                m,
                x='round',
                y='value',
                color='variable',
                barmode='group',
                title="患者情绪与压力水平（分组柱状图）",
                text='label'  # 关键：直接使用我们生成的富文本标签
            )

            # 坐标与阈值线
            fig.update_yaxes(range=[0, 10], tick0=0, dtick=1)
            fig.add_hline(
                y=STRESS_HIGH_RISK,
                line_dash="dash", line_color="red",
                annotation_text="高风险阈值"
            )

            # 文本样式：白色、加粗（通过<b>…</b>）、更大字体；位置在柱子底部
            fig.update_traces(
                textposition="inside",
                insidetextanchor="start",  # 贴近柱底（横轴上方）
                textfont=dict(size=16, color="white")
            )
            # 多数据时避免拥挤，过小则隐藏文本
            fig.update_layout(
                height=300,
                margin=dict(l=30, r=20, t=40, b=20),
                legend_title_text="",
                bargap=0.3 if df.shape[0] == 1 else 0.15,
                uniformtext_minsize=12,
                uniformtext_mode='hide'
            )

            # 固定在页面顶部（可选）
            _inject_sticky_css_once()
            if STICKY_ENABLED:
                st.markdown(f'<div class="{STICKY_CLASS}">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.plotly_chart(fig, use_container_width=True)

        # 干预触发记录
        if st.session_state.stress_model.intervention_triggers:
            st.subheader("干预触发记录")
            for t in st.session_state.stress_model.intervention_triggers:
                st.warning(f"第{t['round']}轮: {t['type']} (压力水平: {t['stress_levels']})")

    # ===== 其余两个 Tab 保持你的原逻辑 =====
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
            fig_radar.update_layout(height=300, margin=dict(l=30, r=20, t=40, b=20))  # 紧凑
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
