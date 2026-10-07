from pytest_llm_assert import assert_behavior


def fake_llm(prompt: str) -> str:
    """一个假的 LLM，用来做离线测试。"""
    if "退款" in prompt:
        return "您好，关于退款政策，我们支持7天无理由退款。"
    if "天气" in prompt:
        return "今天深圳天气晴朗，气温26度。"
    return "抱歉，我不太明白您的问题。"


def test_refund_mentions_policy():
    output = fake_llm("我想退款")
    assert_behavior(output).mentions("退款政策")


def test_weather_mentions_temperature():
    output = fake_llm("今天天气怎么样")
    assert_behavior(output).mentions("气温")

def test_chain_fail():
    output = fake_llm("今天天气怎么样")
    assert_behavior(output).mentions("weather").not_mentions("weather")