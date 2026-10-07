import pytest
from pytest_llm_assert import assert_behavior


def test_tone_empathy():
    output = "非常抱歉给您带来不便，我完全理解您的心情。"
    assert_behavior(output).tone("共情")


def test_tone_professional():
    output = "根据公司退款政策，我们将在3个工作日内处理您的申请。"
    assert_behavior(output).tone("专业")


def test_tone_friendly():
    output = "很高兴为您服务，祝您生活愉快！"
    assert_behavior(output).tone("友好")


@pytest.mark.xfail(reason="故意失败，验证语气检测能识别不匹配")
def test_tone_should_fail():
    output = "今天深圳天气晴朗，气温26度。"
    assert_behavior(output).tone("共情")


def test_tone_chain():
    output = "非常抱歉给您带来不便，我们支持7天无理由退款。"
    (
        assert_behavior(output)
        .mentions("退款")
        .tone("共情")
    )