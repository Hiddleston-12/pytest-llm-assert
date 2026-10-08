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
from example.fake_llm import fake_llm
from pytest_llm_assert import assert_behavior
from example.policies import REFUND_POLICY,SHIPPING_POLICY,COMPLAINT_POLICY
def test_refund_response():
    output = fake_llm("我想退款")
    (
        assert_behavior(output)
        .grounded_in(REFUND_POLICY)     # 没有幻觉
        .mentions("退款政策")            # 提到了关键信息
        .not_mentions("竞品")            # 没有提到竞品
        .tone("共情")                    # 语气合适
    )
``` 
所有断言基于**离线模型**（sentence-transformers + NLI），不需要调用任何 LLM API，CI 里几秒就能跑完。

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



## 技术栈

| 组件 | 用途 |
|---|---|
| pytest | 测试框架 + 插件机制 |
| pytest-html | HTML 报告生成 |
| sentence-transformers | 语义相似度（多语言） |
| transformers | NLI 幻觉检测 |
| torch | 模型推理（CPU） |

所有模型**离线运行**，CI 中不需要 GPU。

---
## 安装
```bash
git clone https://github.com/Hiddleston-12/pytest-llm-assert.git
cd pytest-llm-asser #进入下载的目录
pip install --upgrade
pip install -e .
```
依赖：

- `pytest>=7.0`
- `pytest-html>=4.1.1`
- `sentence-transformers>=2.2.0`
- `transformers>=4.30`
- `huggingface_hub>=1.5.0,<2.0`

首次运行会下载两个模型（约 680MB，只需一次）：

- `paraphrase-multilingual-MiniLM-L12-v2`（多语语义相似度检测模型，约 120MB）
- `mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`（NLI 幻觉检测，约 560MB）

国内可设镜像加速：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```
---

## 模型选择
文本相似度对比：（多语模型）`paraphrase-multilingual-MiniLM-L12-v2`
文本逻辑判断：（多语）`mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`

---
## 快速开始

### 保存基线
```bash
pytest tests/test_customer_service.py --llm-save-baseline -v
```
会在 `.llm_baselines/baseline.json` 记录每条断言的分数和状态：

```json
{
  "test_refund_response::tone::共情": {
    "test": "test_refund_response",
    "assertion": "tone",
    "target": "共情",
    "score": 0.7231,
    "status": "passed"
  }
}
```
---
### 对比基线
```bash
ytest tests/test_customer_service.py --llm-compare-baseline -v
```

检测到漂移时输出：

```text
============================================================
[llm-assert] 检测到 1 处行为漂移：
============================================================

[score_drop] test_refund_response::tone::共情
  基线: score=0.7231, status=passed
  当前: score=0.5122, status=passed
  说明: 分数从 0.7231 下降到 0.5122（下降 29.2%）
```

同时 `pytest` 退出码为 1，可用于 CI 阻断合并。
---
### html报告
```bash
pytest .\tests\test_customer_service.py --llm-compare-baseline --html=reports/report.html --self-contained-html -v
```
报告包含：

- 环境信息（Python 版本、插件列表、rootdir）
- 每条测试的通过/失败状态、耗时
- **断言类型列**（mentions / not_mentions / tone / grounded_in）
- 失败测试的可展开错误详情（含相似度分数）
- 底部的**基线漂移报告**

---
断言失败时的输出

```text
[llm-assert] mentions 断言失败
  目标短语 : 退款政策
  实际输出 : 今天深圳天气晴朗，气温26度。
  相似度   : 0.2341（阈值 0.7）
```

错误信息包含**目标、实际输出、相似度分数、阈值**，方便调试。

---
## 详细用法
### 语义提及 `mentions`

```python
assert_behavior(output).mentions("退款政策", threshold=0.7)
```

判断输出是否**在语义上**提到了目标，不要求字面一致。

| 输出 | 目标 | 相似度 | 结果 |
|---|---|---|---|
| "我们支持7天无理由退款" | "退款政策" | 0.82 | ✅ |
| "我们支持7天无理由退货" | "退款政策" | 0.75 | ✅ |
| "今天天气很好" | "退款政策" | 0.23 | ❌ |

### 语义不包含 `not_mentions`

```python
assert_behavior(output).not_mentions("竞品")
```

判断输出是否**没有**提到目标。常用于屏蔽敏感词、竞品名。

### 幻觉检测 `grounded_in`

```python
REFUND_POLICY = "我们支持7天无理由退款。定制商品不支持无理由退款。"
assert_behavior(output).grounded_in(REFUND_POLICY)
```

用 NLI 模型判断输出是否被上下文**蕴含**。如果输出编造了上下文里没有的内容，断言失败。

**注意**：`grounded_in` 只检查**事实性陈述**，不检查情感表达。如果输出里既有事实又有道歉，建议只把事实部分喂给 `grounded_in`，道歉部分用 `.tone()` 单独测。

### 语气检测 `tone`

```python
assert_behavior(output).tone("共情")
```

支持的语气：`共情`、`专业`、`友好`、`正式`、`中性`

原理：每种语气配多句参考模板，计算输出和每个模板的语义相似度，取最高分作为该语气的得分。

### 链式调用

```python
(
    assert_behavior(output)
    .grounded_in(policy)
    .mentions("退款")
    .not_mentions("竞品")
    .tone("共情")
)
```

**注意**：链式调用中，一旦某个断言失败，后面的断言不会执行。如果需要所有断言都跑一遍，可以拆开写：

```python
ab = assert_behavior(output, recorder, test_name)
errors = []
for check in [
    lambda: ab.grounded_in(policy),
    lambda: ab.mentions("退款"),
    lambda: ab.tone("共情"),
]:
    try:
        check()
    except AssertionError as e:
        errors.append(str(e))
if errors:
    raise AssertionError("\n".join(errors))
```
---

## CI/CD

项目已接入 GitHub Actions。每次 push 自动执行：

1. 安装依赖
2. 下载模型（缓存复用）
3. 运行测试 + 基线对比
4. 生成 HTML 报告
5. 检测到漂移时阻断

配置文件：`.github/workflows/test.yml`

---

## License

MIT
	