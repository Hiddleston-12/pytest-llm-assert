"""
模拟客服回答的程序，负责根据用户提问输出回答
"""

def fake_llm(prompt:str)->str:
    prompt = prompt.strip()
    if "定制" in prompt and "退款" in prompt:
        return (
            "您好，定制的产品不接受七天无理由退款。"
            "如果是质量问题，我们可以安排退换"
        )

    if "天气" in prompt:#使用不相干的话题，保证ground_in能判断
        return "今日气温26度，天气晴朗。"

    if "退款" in prompt:
        return (
            "我们支持7天无理由退款，您可以在订单页面申请退款。"
            "非常抱歉没能满足您的需求，我完全理解您的心情。"    #加入ungrounded，制造漂移

        )
    if "发货"in prompt or "快递" in prompt:
        return (
            "您好，您的订单已发货，预计3个工作日内送达。"
            "您可以在订单详情页查看物流信息。"
        )
    if  "竞品" in prompt:#使用“竞品来验证not_mention能抓到”
        return "我们的价格比竞品便宜。"

    if "其他家" in prompt:
        return "我们的价格已经是全网最低价了，建议您选择我们。"

    if "投诉" in prompt:#故意语气冷淡，验证tone
        return "收到投诉，等待处理。"



    return "我不太明白，请您换一个说法试试。"