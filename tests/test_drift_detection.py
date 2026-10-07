from pytest_llm_assert.baseline import BaselineCompare
def test_compare_score():
    baseline={
        "t::mentions::退款":{
            "test":"t",
            "assertion":"mentions",
            "target": "退款",
            "score": 0.9,
            "status": "passed",
            "timestamp": '',
        }
    }
    current={
            "t::mentions::退款": {
            "test": "t",
            "assertion": "mentions",
            "target": "退款",
            "score": 0.6,
            "status": "passed",
            "timestamp": '',
        }
    }
    from pytest_llm_assert import baseline as bl
    original_load=bl._load_baseline
    bl._load_baseline=lambda :baseline#模块里的 _load_baseline 函数替换成一个匿名函数，它不接受任何参数，永远返回变量 baseline（也就是在测试里上方手写的那份假数据）。
    try:
        comparator=BaselineCompare(current)
        drifts=comparator.compare()
        assert len(drifts)==1
        assert drifts[0]["type"]=="score_drop"
    finally:
        bl._load_baseline=original_load

def test_compare_status():
    baseline={
        "t::tone::专业":{
            "test":"t",
            "assertion":"tone",
            "target": "共情",
            "score": 0.9,
            "status": "passed",
            "timestamp": '',
        }
    }
    current={
            "t::tone::专业  ": {
            "test": "t",
            "assertion": "tone",
            "target": "专业",
            "score": 0.6,
            "status": "failed",
            "timestamp": '',
        }
    }
    from pytest_llm_assert import baseline as bl
    original_load=bl._load_baseline
    bl._load_baseline=lambda :baseline
    try:
        comparator=BaselineCompare(current)
        drifts=comparator.compare()
        print(drifts)
        assert len(drifts)==1
        assert any(d["type"] == "status_regression" for d in drifts)
    finally:
        bl._load_baseline=original_load
