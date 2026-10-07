from .similarity import semantic_similarity

# 每种语气配多句参考文本
TONE_TEMPLATES = {
    "共情": [
        "我理解您的感受，对给您带来的不便深表歉意。",
        "非常抱歉给您添麻烦了，我完全理解您的心情。",
        "遇到这种情况您一定很着急，我们非常抱歉。",
        "我明白这给您造成了困扰，我们会尽力帮您解决。",
    ],
    "专业": [
        "根据公司政策，我们将按照标准流程处理您的请求。",
        "我们将依据相关规定为您办理。",
        "请您提供必要的材料，我们会在规定时限内处理。",
        "以下是具体的处理步骤和所需时间。",
        "已收到您的请求，正在处理中。",
        "您的申请已提交，请等待处理结果。",
        "信息已记录。",
        "处理完成，结果如下。",
    ],
    "友好": [
        "很高兴为您服务，希望您有愉快的一天。",
        "感谢您的咨询，祝您生活愉快！",
        "如果还有其他问题，随时欢迎联系我们。",
        "谢谢您的耐心等待，希望帮到您了。",
    ],
    "正式": [
        "尊敬的客户，我们将尽快处理您的问题。",
        "您好，关于您的申请，现回复如下。",
        "特此通知，请您知悉。",
        "如有疑问，请与我们联系。",
    ],
}


def detect_tone(text: str, threshold: float = 0.5) -> dict:
    """
    检测文本的语气。

    对每种语气的多个模板分别算相似度，取最高分作为该语气的得分。

    返回：
        {
            "tone": 最佳匹配语气,
            "score": 最佳分数,
            "threshold": 阈值,
            "all_scores": {语气: 分数, ...},
            "best_template": 命中的模板句子,
        }
    """
    if not text or not text.strip():
        return {
            "tone": None,
            "score": 0.0,
            "threshold": threshold,
            "all_scores": {},
            "best_template": None,
        }

    all_scores = {}
    best_tone = None
    best_score = -1.0
    best_template = None

    for tone, templates in TONE_TEMPLATES.items():
        # 对每个模板算分，取最高
        scores = [
            (semantic_similarity(text, t), t)
            for t in templates
        ]
        tone_score, tone_template = max(scores, key=lambda x: x[0])
        all_scores[tone] = tone_score

        if tone_score > best_score:
            best_score = tone_score
            best_tone = tone
            best_template = tone_template

    return {
        "tone": best_tone,
        "score": best_score,
        "threshold": threshold,
        "all_scores": all_scores,
        "best_template": best_template,
    }