import streamlit as st
from services.deepseek_client import DeepSeekClient
from utils.parsing import parse_ai_json


def build_system_prompt():
    history_preview = "\n".join([f"{h[0]}: {h[1]}" for h in st.session_state.history[-4:]])
    return f"""你是一个32岁不孕症患者小林，正在接受护理人员沟通训练。\n\n核心规则：\n1. 用第一人称简短回复（1-2句话）\n2. 必须输出严格的JSON格式，不要有其他文字\n3. 根据护士话术调整情绪值（0.0-1.0）\n4. 同时评估护士的护理沟通表现\n\nJSON格式示例：\n{{\n  \"patient_response\": \"我心情很沉重，不知道还能坚持多久\",\n  \"emotion_update\": {{\n    \"anxiety\": 0.8,\n    \"sadness\": 0.7,\n    \"hope\": 0.2\n  }},\n  \"nurse_evaluation\": {{\n    \"empathy_accuracy_rate\": 75.0,\n    \"strategy_adaptation_rate\": 82.0,\n    \"overall_competency\": 78.5,\n    \"clinical_standard_met\": false,\n    \"detected_strategy\": \"情感确认\",\n    \"analysis\": \"护士表现出一定的共情能力，但策略选择可以更精准\"\n  }}\n}}\n\n评估标准：\n- empathy_accuracy_rate: 护士共情准确率(0-100分)，看是否准确识别和回应患者情绪\n- strategy_adaptation_rate: 沟通策略适配度(0-100分)，策略是否适合当前情况和压力水平  \n- overall_competency: 整体护理沟通能力(0-100分)\n- clinical_standard_met: 是否达到临床标准(共情≥85%且策略≥90%)\n- detected_strategy: 识别的护理策略类型\n- analysis: 简短的专业分析\n\n当前场景：{st.session_state.training_scenario}\n对话历史：{history_preview}\n护士刚说："""


def render_history():
    st.header("💬 训练对话")
    for speaker, text, metrics in st.session_state.history:
        with st.chat_message("user" if speaker == "护士" else "assistant"):
            st.write(f"**{speaker}:** {text}")
            if metrics and speaker == "护士" and st.session_state.api_evaluation:
                api_scores = st.session_state.api_evaluation
                st.caption(
                    f"共情准确率: {api_scores['empathy_accuracy_rate']:.1f}% | "
                    f"策略适配度: {api_scores['strategy_adaptation_rate']:.1f}% | "
                    f"使用策略: {api_scores.get('detected_strategy', '未识别')}"
                )


def handle_input(api_key: str):
    prompt = st.chat_input("请输入你的沟通话术...")
    if not prompt:
        return

    st.session_state.conversation_round += 1
    st.session_state.history.append(("护士", prompt, None))

    sys_prompt = build_system_prompt() + prompt
    client = DeepSeekClient(api_key)

    with st.chat_message("user"):
        st.write(f"**护士:** {prompt}")

    with st.chat_message("assistant"):
        with st.spinner("小林正在思考..."):
            try:
                ai_content = client.chat(sys_prompt)
                with st.expander("🔍 调试信息"):
                    st.text(f"原始API响应: {ai_content}")

                parsed = parse_ai_json(ai_content)
                patient_response = parsed.get("patient_response", "我...有些不知道该说什么")
                base_emotion = parsed.get("emotion_update", {"anxiety": 0.6, "sadness": 0.5, "hope": 0.3})
                nurse_eval = parsed.get("nurse_evaluation", {})

                # 关键词检测与情绪调整
                detected_keywords, keyword_effect = st.session_state.stress_model.detect_keywords(patient_response)
                adjusted = {
                    'anxiety': max(0, min(1, base_emotion.get('anxiety', 0.6) + keyword_effect.get('anxiety', 0))),
                    'sadness': max(0, min(1, base_emotion.get('sadness', 0.5) + keyword_effect.get('sadness', 0))),
                    'hope': max(0, min(1, base_emotion.get('hope', 0.3) + keyword_effect.get('hope', 0)))
                }
                assess = st.session_state.stress_model.assess_emotion_pattern(adjusted, st.session_state.conversation_round)
                st.session_state.assessment_history.append(assess)

                nurse_metrics = {
                    'empathy': nurse_eval.get('empathy_accuracy_rate'),
                    'adaptation': nurse_eval.get('strategy_adaptation_rate'),
                    'strategy': nurse_eval.get('detected_strategy', '未识别')
                }
                st.session_state.history[-1] = ("护士", prompt, nurse_metrics)
                st.session_state.history.append(("病人小林", patient_response, None))
                st.session_state.emotions.append(adjusted)
                st.session_state.api_evaluation = nurse_eval or st.session_state.api_evaluation

                st.write(f"**病人小林:** {patient_response}")
                if detected_keywords:
                    st.info("🔍 检测到情绪关键词: " + ", ".join([k['keyword'] for k in detected_keywords]))
                if assess['requires_intervention']:
                    st.error(f"🚨 需要干预: {assess['intervention_type']}")

                if nurse_eval:
                    st.success(
                        f"📊 本轮评估: 共情{nurse_eval.get('empathy_accuracy_rate', 0):.1f}% | "
                        f"策略{nurse_eval.get('strategy_adaptation_rate', 0):.1f}% | "
                        f"压力水平{assess['stress_level']}/10"
                    )
                    st.info(
                        f"💡 AI分析: {nurse_eval.get('analysis', '')} | "
                        f"策略类型: {nurse_eval.get('detected_strategy', '未识别')}"
                    )
                    st.info("📈 临床标准: " + ("✅已达成" if nurse_eval.get('clinical_standard_met') else "❌未达成"))

            except Exception as e:
                err = f"发生错误: {str(e)}"
                st.session_state.history.append(("系统", err, None))
                st.error(f"**系统:** {err}")

    st.rerun()