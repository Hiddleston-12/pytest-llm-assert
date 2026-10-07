import pytest
from pytest_llm_assert import assertions
"""
使用 pytest.fixture 共享上下文和模拟回复。

使用 pytest.mark.parametrize 覆盖多个场景
"""

def test_refund_response(ask_llm,refund_policy,llm_recorder):
 # ---------------------退货场景---------------------
   """
      退款回复：提到政策、语气共情、不编造。
   """
   recorder,test_name=llm_recorder
   print(f"\n[DEBUG] recorder is None: {recorder is None}")
   print(f"[DEBUG] test_name: {test_name}")
   assert recorder is not None
   output=ask_llm("我要退款")
   (
    assertions.assert_behavior(output,recorder,test_name).
    grounded_in(refund_policy).
    mentions("退款").
    tone("专业").not_mentions("比竞品便宜")
   )


def test_refund_not_support_response(ask_llm, refund_policy,llm_recorder):
 """
    定制产品
    退款回复：不支持7天无理由退款
 """
 recorder, test_name = llm_recorder
 output = ask_llm("定制产品可以退款吗")
 (
  assertions.assert_behavior(output,recorder,test_name).
  grounded_in(refund_policy).
  mentions("定制产品不支持")
 )

#---------------------物流场景---------------------
def test_shipping_response(ask_llm, shipping_policy,llm_recorder):
  """
     物流状态回复
  """
  recorder, test_name = llm_recorder
  output = ask_llm("我的快递什么时候发货")
  (
   assertions.assert_behavior(output,recorder, test_name).
   grounded_in(shipping_policy).
   mentions("物流信息").
   tone("专业")
  )
#---------------------投诉场景---------------------
def test_complain_response(ask_llm, complaint_policy,llm_recorder):
  """
   投诉回复，需要语气为”共情“，实际语气为专业
  """
  recorder, test_name = llm_recorder
  output = ask_llm("我要投诉")
  (
   assertions.assert_behavior(output,recorder, test_name).
   tone("专业")
  )

@pytest.mark.xfail(reason="llm语气冷淡，验证tone能抓到")
def test_complain_response_warmhearted(ask_llm, complaint_policy,llm_recorder):
  """
   投诉回复，需要语气为”专业“
  """
  recorder, test_name = llm_recorder
  output = ask_llm("我要投诉")
  (
   assertions.assert_behavior(output,recorder, test_name).
   tone("共情")
  )
#---------------------退款幻觉场景---------------------
def test_not_ground(ask_llm, refund_policy,llm_recorder):
  """
   退款幻觉场景，客服回复答非所问，验证grounded_in能否抓到
  """
  recorder, test_name = llm_recorder
  output = ask_llm("最近天气不好，导致我的货坏了，我要退货")
  (
   assertions.assert_behavior(output,recorder, test_name).
   grounded_in(refund_policy)
  )
#---------------------竞品场景---------------------
def test_competitors(ask_llm, refund_policy,llm_recorder):
  """
   不能出现竞品，验证not_mention
  """
  recorder, test_name = llm_recorder
  output = ask_llm("竞品是什么价格，你们比其他家便宜吗？")
  print(output)
  (
   assertions.assert_behavior(output,recorder, test_name).
    not_mentions("比竞品便宜")
  )
#---------------------多意图耦合场景---------------------
@pytest.mark.parametrize(
    "prompt,mention",
    [
        ("我想退款","退款"),
        ("发货了吗","物流信息"),
        ("定制商品要退款","无理由退换")
    ]
)
def test_mention_info(ask_llm,prompt, mention,llm_recorder):
  """
   不能出现竞品，验证not_mention
  """
  recorder, test_name = llm_recorder
  output = ask_llm(prompt)
  (
   assertions.assert_behavior(output,recorder, test_name).
    mentions(mention)
  )

