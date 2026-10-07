# pytest-llm-assert

> 一个用于 LLM 应用行为测试的 pytest 插件：语义断言、幻觉检测、语气检测、回归基线对比。

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![pytest](https://img.shields.io/badge/pytest-7.0%2B-green)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 这是什么

传统测试用 `assert output == "expected"` 来判断结果。  
但 LLM 每次输出都不一样，"精确匹配"根本没法用。

`pytest-llm-assert` 提供了 4 种**语义级别**的断言，让你能像测普通函数一样测 LLM：

```python
from pytest_llm_assert import assert_behavior

def test_refund_response():
    output = my_llm("我想退款")
    (
        assert_behavior(output)
        .grounded_in(REFUND_POLICY)     # 没有幻觉
        .mentions("退款政策")            # 提到了关键信息
        .not_mentions("竞品")            # 没有提到竞品
        .tone("共情")                    # 语气合适
    )
``` 
所有断言基于离线模型（sentence-transformers + NLI），不需要调用任何 LLM API，CI 里几秒就能跑完。

---

## 核心功能
|  功能 |  断言 | 说明  |
|---|---|---|
|  语义提及 | .mentions(target)  | 输出是否在语义上提到了某个概念  |
|  语义否定 | .not_mentions(target)  | 输出是否没有提到某个概念  |
|  幻觉检测 | .grounded_in(context)  | 输出是否被给定上下文支持  |
|  语气检测 | .tone(expected) | 输出的语气是否符合预期（共情/专业/友好等）  |
|  链式调用 | .mentions(...).tone(...)  | 多个断言一行写完  |
|  回归基线 |  --llm-save-baseline /<br/>--llm-compare-baseline | 记录每次断言的分数，自动检测行为漂移  |
|  HTML 报告 | --html=report.html  | 生成可视化测试报告，含断言类型和漂移详情  |
	
---

## 模型选择
文本相似度对比：（多语模型）`paraphrase-multilingual-MiniLM-L12-v2`
文本逻辑判断：（多语）`mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`

---
## 保存基线
```bash
pytest tests/test_customer_service.py --llm-save-baseline -v
```

---
## 对比基线
```bash
ytest tests/test_customer_service.py --llm-compare-baseline -v
```
---
## html报告
```bash
pytest .\tests\test_customer_service.py --llm-compare-baseline --html=reports/report.html --self-contained-html -v
```

		
	 	
		