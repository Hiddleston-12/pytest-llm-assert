#from pytest_llm_assert import assert_behavior

from pytest_llm_assert import assert_behavior


CONTEXT = (    "我们支持7天无理由退款。"
    "但是定制商品不支持无理由退款，质量问题可以退换。"
    "退款申请需在订单页面提交，3个工作日内处理。"
    "已收到申请，请等待处理")



def test_grounded_pass():
    output = "我们支持7天无理由退款，您可以在订单页面申请退款。非常抱歉没能满足您的需求，我完全理解您的心情。"
    g=assert_behavior(output).grounded_in(CONTEXT)
    print("$" * 60)
    print(g._record().record["status"])
    print("$" * 60)

def test_grounded_contradiction():
    output = "我们不支持退款。"
    assert_behavior(output).grounded_in(CONTEXT)





def test_grounded_neutral():
    output = "退款需要人工审核。"
    assert_behavior(output).grounded_in(CONTEXT)


def test_grounded_chain():
    output = "我们支持7天无理由退款。"
    (
        assert_behavior(output)
        .grounded_in(CONTEXT)
        .not_mentions("竞品")
    )