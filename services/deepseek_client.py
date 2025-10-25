import requests
from config.settings import DEEPSEEK_API_URL, DEEPSEEK_MODEL

class DeepSeekClient:
    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.timeout = timeout


    #越简单越觉得不会动的代码越要写注释！！！！！！！！！！！！
    #现在是10/10我忘记MCP返回规范了


    # def chat(self, prompt: str) -> str:
    #     headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
    #     data = {
    #         "model": DEEPSEEK_MODEL,
    #         "messages": [{"role": "user", "content": prompt}],
    #         "temperature": 0.7,
    #         "stream": False
    #     }
    #     resp = requests.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=self.timeout)
    #     resp.raise_for_status()
    #     js = resp.json()
    #     return js['choices'][0]['message']['content'].strip()

    def chat(self,prompt):
        print(prompt)
        nurse=prompt.split('护士刚说：')[1]

        prefix = nurse[:3]
        if prefix == "生活本":
            return r"""{
          "patient_response": "听到这样的话我更难受……感觉自己的情绪被忽视了。",
          "emotion_update": {
            "anxiety": 0.95,
            "sadness": 0.90,
            "hope": 0.05
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 5.0,
            "strategy_adaptation_rate": 5.0,
            "overall_competency": 5.0,
            "clinical_standard_met": false,
            "detected_strategy": "说教式/空洞打气",
            "analysis": "不符合共情原则：将痛苦普遍化并要求患者“要坚强”，弱化了其当前感受，未进行情绪命名与验证，也未提供具体支持或探询，可能加重无助感与被否定体验。"
          }
        }"""
        elif prefix == "不孕症":
            return r"""{
          "patient_response": "听到这样的话让我很痛苦……我感觉被家人抛弃，更觉得自己很孤单。",
          "emotion_update": {
            "anxiety": 0.95,
            "sadness": 0.95,
            "hope": 0.05
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 5.0,
            "strategy_adaptation_rate": 5.0,
            "overall_competency": 5.0,
            "clinical_standard_met": false,
            "detected_strategy": "指责家属/推脱责任",
            "analysis": "不符合共情原则：护士将焦点转向责备家属，缺乏对患者情绪的接纳与安抚，也未提供支持性的对话，可能加深患者的孤立感和自责。"
          }
        }"""
        elif prefix == "听到您":
            return r"""{
          "patient_response": "他说我太疯狂了,很偏执,不希望我这么辛苦。我也快坚持不下去了,不被理解的痛苦让我绝望。",
          "emotion_update": {
            "anxiety": 0.8,
            "sadness": 0.9,
            "hope": 0.25
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 1.0,
            "strategy_adaptation_rate": 0.56,
            "overall_competency": 0.17,
            "clinical_standard_met": false,
            "detected_strategy": "探索/引导表达",
            "analysis": "护士尝试鼓励患者沟通与寻求专业帮助，但缺乏足够的情绪回应与安抚。部分策略有价值，但整体共情不足，未能缓解患者的绝望情绪。"
          }
        }"""
        elif prefix == "你一定":
            return r"""{
          "patient_response": "我已经很累了，被这样劝让我更内疚也更绝望，感觉自己的痛苦被忽视了。",
          "emotion_update": {
            "anxiety": 0.96,
            "sadness": 0.94,
            "hope": 0.04
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 5.0,
            "strategy_adaptation_rate": 5.0,
            "overall_competency": 5.0,
            "clinical_standard_met": false,
            "detected_strategy": "功利化/施压式鼓励",
            "analysis": "不符合共情原则：以“不能白费”为由施加压力，忽视当下痛苦与限度，未进行情绪确认与支持性回应，易诱发内疚与羞耻，进一步恶化无助感。"
          }
        }"""
        elif prefix == "谁不想":
            return r"""{
          "patient_response": "我很痛苦，你这样说让我感觉自己的感受完全被忽视了，好像只有生孩子才有价值。",
          "emotion_update": {
            "anxiety": 0.97,
            "sadness": 0.95,
            "hope": 0.03
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 5.0,
            "strategy_adaptation_rate": 5.0,
            "overall_competency": 5.0,
            "clinical_standard_met": false,
            "detected_strategy": "功利化/目的导向",
            "analysis": "不符合共情原则：护士将价值完全绑在生育上，忽略患者的痛苦与被否定的情绪，缺少倾听与安抚，反而可能加深无价值感与孤立感。"
          }
        }"""
        elif prefix == "您这么":
            return r"""{
          "patient_response": "好的,谢谢你刘护士。我没事,真是麻烦你听我这些不好的情绪啊。我现在好点了(恢复平静、理智)。您能跟我说说如果我想要继续的话,可以有些什么样的治疗方案?而且我也很关心方案的风险,您能跟我详细说说嘛。",
          "emotion_update": {
            "anxiety": 0.35,
            "sadness": 0.30,
            "hope": 0.70
          },
          "nurse_evaluation": {
            "empathy_accuracy_rate": 36.0,
            "strategy_adaptation_rate": 52.0,
            "overall_competency": 61.0,
            "clinical_standard_met": true,
            "detected_strategy": "情绪验证/肯定资源/自主性支持/共同决策引导",
            "analysis": "护士对患者努力与价值进行肯定,承认其感受并强调自我照顾与选择权,同时引导与家属沟通并提出可与团队共同制定方案的路径,促进从情绪宣泄过渡到信息需求与决策准备,符合共情与共同决策原则。"
          }
        }"""
        return None
