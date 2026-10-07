import pytest
from example.fake_llm import fake_llm
from example.policies import REFUND_POLICY,SHIPPING_POLICY,COMPLAINT_POLICY
from pytest_html import extras as html_extras
from pytest_llm_assert.baseline import BaselineRecorder
@pytest.fixture
def refund_policy():
    return REFUND_POLICY

@pytest.fixture
def shipping_policy():
    return SHIPPING_POLICY

@pytest.fixture
def complaint_policy():
    return COMPLAINT_POLICY

@pytest.fixture
def llm_recorder(request):
    recorder=request.config._llm_recorder
    return recorder,request.node.name
@pytest.fixture
def ask_llm():
    """
    工厂函数，返回一个可调用的函数，方便测试的时候使用
    """
    def _ask(prompt:str)->str:
        return fake_llm(prompt)
    return _ask

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item,call):
    outcome=yield
    report=outcome.get_result()

    if call.when!="call":
        return
    config=item.config
    recorder=getattr(config,"_llm_recorder",None)
    if recorder is None:
        report.llm_assertion_types= set()
        return
    # key 格式是 "函数名::断言类型::目标"
    # item.nodeid 是 "tests/xxx.py::函数名"，取最后一段
    func_name=item.nodeid.split("::")[-1]
    prefix=func_name+"::"
    types=set()
    for key,rec in recorder.records.items():
        if key.startswith(prefix):
            types.add(rec["assertion"])
    report.llm_assertion_types=types



@pytest.fixture(autouse=True)
def project_link(extras):
    extras.append(html_extras.url("https://example.com", name="项目主页"))