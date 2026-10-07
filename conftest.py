import pytest
#from py.xml import html
@pytest.hookimpl(tryfirst=True)
def pytest_html_results_table_header(cells):#钩子函数
    cells.insert(2,'<th>断言类型</th>')

@pytest.hookimpl(tryfirst=True)
def pytest_html_results_table_row(report,cells):
    #从测试名判断断言类型
    #print(f"[DEBUG] pytest_html_results_table_row 被调用了: {report.nodeid}")
    if report.when!="call":
        cells.insert(2,"<td>-</td>")
        return
    types=getattr(report,"llm_assertion_types",set())
    if types:
        assertion_type=",".join(sorted(types))
    else:
        assertion_type="-"
    cells.insert(2,f"<td>{assertion_type}</td>")