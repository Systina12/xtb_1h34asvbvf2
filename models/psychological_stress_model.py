from datetime import datetime

class PsychologicalStressModel:
    """基于压力-适应理论的心理应激模型"""
    def __init__(self, keyword_rules: dict | None = None):
        self.emotion_history = []
        self.intervention_triggers = []
        self.session_metrics = {
            'negative_emotion_duration': 0,
            'emotion_volatility_count': 0,
            'intervention_effectiveness': []
        }
        self.keyword_rules = keyword_rules or {}

    def calculate_stress_level(self, emotions: dict) -> int:
        anxiety = emotions.get('anxiety', 0)
        sadness = emotions.get('sadness', 0)
        hope = emotions.get('hope', 0)
        stress_score = (anxiety * 0.5 + sadness * 0.4 - hope * 0.3) * 10
        return max(1, min(10, int(round(stress_score))))

    def detect_keywords(self, text: str):
        detected_keywords = []
        total_effect = {"anxiety": 0, "sadness": 0, "hope": 0}
        for intensity, rule in self.keyword_rules.items():
            for kw in rule.get("keywords", []):
                if kw in text:
                    detected_keywords.append({
                        "keyword": kw,
                        "intensity": intensity,
                        "effect": rule.get("effect", {})
                    })
                    for emo, val in rule.get("effect", {}).items():
                        total_effect[emo] = total_effect.get(emo, 0) + val
        return detected_keywords, total_effect

    def assess_emotion_pattern(self, current_emotions: dict, conversation_round: int):
        stress_level = self.calculate_stress_level(current_emotions)
        assessment = {
            'timestamp': datetime.now(),
            'round': conversation_round,
            'emotions': current_emotions,
            'stress_level': stress_level,
            'requires_intervention': False,
            'intervention_type': None
        }
        if len(self.emotion_history) >= 2:
            recent_stress = [e['stress_level'] for e in self.emotion_history[-2:]] + [stress_level]
            if all(s >= 7 for s in recent_stress):
                assessment['requires_intervention'] = True
                assessment['intervention_type'] = 'crisis_support'
                self.intervention_triggers.append({
                    'type': 'prolonged_high_stress',
                    'round': conversation_round,
                    'stress_levels': recent_stress
                })
        self.emotion_history.append(assessment)
        return assessment