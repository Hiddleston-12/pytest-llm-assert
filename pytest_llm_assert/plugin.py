from pydoc import html
#import pytest_html
from .baseline import BaselineRecorder,BaselineCompare
import pytest
import sys
_drift_report_html=""

def pytest_addoption(parser):
    parser.addoption(
        "--llm-assert",
        action="store_true",
        default=False,
        help="启用 LLM 行为断言插件（当前仅用于验证插件加载）",
    )
    parser.addoption(
        "--llm-save-baseline",
        action="store_true",
        default=False,
        help="保存本次结果为基线",
    )
    parser.addoption(
        "--llm-compare-baseline",
        action="store_true",
        default=False,
        help="与基线结果对比，检测漂移",
    )

def pytest_configure(config):#这里没看懂，要问一下，config具体传入了什么东西
    """config 是 pytest 传进来的 Config 对象，代表整个 pytest 会话的全局配置和状态。
    它是 pytest 内部创建的一个对象，包含：

    命令行参数（可以通过 config.getoption("--xxx") 读取）

    插件管理器（config.pluginmanager）

    根目录、ini 文件配置

    各种钩子、缓存、日志等"""
    config._llm_recorder=BaselineRecorder()#给config动态加熟悉，先init一个空字典
    config._llm_compare = config.getoption("--llm-compare-baseline")#为什么config就能有自己的getoption函数了，这个函数能干什么





def pytest_report_header(config):
    if config.getoption("--llm-assert"):
        return "llm-assert:enabled"
    return None

def pytest_sessionfinish(session,exitstatus):
    """钩子函数，传参是固定的"""
    global _drift_report_html
    config=session.config
    import os
    recorder=getattr(config,"_llm_recorder",None)#getattr函数：从config里读取“--llm-recorder”属性，若没有该属性不会报错
    # sys.stderr.write(f"\n[DEBUG] sessionfinish: recorder={recorder is not None}\n")
    # sys.stderr.write(f"[DEBUG] cwd={os.getcwd()}\n")
    # sys.stderr.write(f"[DEBUG] save option={config.getoption('--llm-save-baseline')}\n")
    # sys.stderr.flush()

    if recorder is None:
        return
    #drift_report=None
    # sys.stderr.write(f"\n[DEBUG] recorder.records 共 {len(recorder.records)} 条\n")
    # sys.stderr.flush()
    if config.getoption("--llm-save-baseline"):
        recorder.save()#写入baseline的结果json

    if config.getoption("--llm-compare-baseline"):
        # sys.stderr.write(f"[DEBUG] 准备对比，records={len(recorder.records)} 条\n")
        # sys.stderr.flush()
        comparator=BaselineCompare(recorder.records)
        drifts=comparator.compare()
        report_text=comparator.report()
        #print(comparator.report())
        if drifts:
            session.exitstatus=1
        _drift_report_html=(
            f"<h2>LLM 基线漂移测试报告</h2>"
            f"<pre style='white-space:pre-warp'>{report_text}</pre>"
        )



def pytest_html_results_summary(prefix,summary,postfix):
    if _drift_report_html:
        prefix.append(_drift_report_html)