import streamlit as st
from models.psychological_stress_model import PsychologicalStressModel
from utils.text_rules import KEYWORD_RULES
from config.settings import DEFAULT_TARGET_ADAPT, DEFAULT_TARGET_EMPATHY

SESSION_KEYS = {
    "history": [],
    "emotions": [],
    "stress_model": None,
    "assessment_history": [],
    "training_scenario": "标准场景",
    "conversation_round": 0,
    "api_evaluation": None,
    "targets": {"empathy": DEFAULT_TARGET_EMPATHY, "adapt": DEFAULT_TARGET_ADAPT}
}

def ensure_state():
    for k, v in SESSION_KEYS.items():
        if k not in st.session_state:
            st.session_state[k] = v if k != "stress_model" else PsychologicalStressModel(KEYWORD_RULES)
    if st.session_state.get("stress_model") is None:
        st.session_state.stress_model = PsychologicalStressModel(KEYWORD_RULES)


