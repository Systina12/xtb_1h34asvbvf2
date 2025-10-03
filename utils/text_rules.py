KEYWORD_RULES = {
    "高强度负面": {
        "keywords": ["绝望", "想死", "撑不下去", "崩溃", "彻底失败"],
        "effect": {"anxiety": +0.3, "sadness": +0.4, "hope": -0.3}
    },
    "中强度负面": {
        "keywords": ["痛苦", "难过", "害怕", "压力", "难受"],
        "effect": {"anxiety": +0.2, "sadness": +0.2, "hope": -0.15}
    },
    "低强度负面": {
        "keywords": ["有点担心", "不太舒服", "有些紧张"],
        "effect": {"anxiety": +0.1, "sadness": +0.1, "hope": -0.05}
    },
    "正面关键词": {
        "keywords": ["好转", "希望", "有信心", "谢谢", "舒服", "理解"],
        "effect": {"hope": +0.2, "anxiety": -0.1, "sadness": -0.1}
    }
}