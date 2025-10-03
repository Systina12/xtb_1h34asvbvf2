import json

def extract_json_block(text: str) -> str:
    cleaned = text.replace('```json', '').replace('```', '').strip()
    s, e = cleaned.find('{'), cleaned.rfind('}')
    if s == -1 or e == -1 or e <= s:
        return cleaned
    return cleaned[s:e+1]

DEFAULT_PAYLOAD = {
    "patient_response": "我现在心情很复杂，感觉有些焦虑...",
    "emotion_update": {"anxiety": 0.7, "sadness": 0.6, "hope": 0.2},
    "nurse_evaluation": {
        "empathy_accuracy_rate": 50.0,
        "strategy_adaptation_rate": 55.0,
        "overall_competency": 52.5,
        "clinical_standard_met": False,
        "detected_strategy": "基础沟通",
        "analysis": "JSON解析失败，使用默认评估"
    }
}

def parse_ai_json(text: str) -> dict:
    try:
        block = extract_json_block(text)
        return json.loads(block)
    except Exception:
        return DEFAULT_PAYLOAD.copy()