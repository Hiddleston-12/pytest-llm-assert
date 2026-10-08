import json
from datetime import datetime
from pathlib import Path
import sys
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_DIR = _PROJECT_ROOT / ".llm_baselines"
BASELINE_FILE = BASELINE_DIR / "baseline.json"
#分数下降超过该阈值，视为漂移
SCORE_DROP_THRESHOLD=0.10

def _load_baseline()->dict:
    if not BASELINE_DIR.exists():
        return {}
    with open(BASELINE_FILE,encoding="utf-8") as f:
        return json.load(f)

def _save_baseline(data:dict)->None:
    BASELINE_DIR.mkdir(exist_ok=True)
    with open(BASELINE_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)

class BaselineRecorder:
    """记录本次运行从所有断言结果"""
    def __init__(self):
        self.records:dict={}

    def record(self,test_name:str,assertion:str,target:str,score:float,status:str):
        key=f"{test_name}::{assertion}::{target}"
        self.records[key]={
            "test":test_name,
            "assertion":assertion,
            "target":target,
            "score":round(score,4),
            "status":status,
            "timestamp":datetime.now().isoformat(timespec="seconds"),
        }
    def save(self):
        _save_baseline(self.records)
        print(f"\n[llm-assert] 基线已保存到 {BASELINE_FILE} （共{len(self.records)}条）")


class BaselineCompare:
    """对比基线和本次结果，检测漂移"""
    def __init__(self,current:dict):
        self.current=current
        self.baseline=_load_baseline()
        self.drifts:list=[]#记录漂移具体信息

    def compare(self):
        """针对不同断言函数的表现，逐条对比，收集所有漂移:状态转变、分数下跌"""
        #sys.stderr.write("\n>>> compare() 被调用了！\n")
        #sys.stderr.flush()  compare 确认被调用
        import sys
        # sys.stderr.write(f"\n=== baseline keys ({len(self.baseline)}) ===\n")
        # for k in self.baseline:
        #     sys.stderr.write(f"  {k}\n")
        # sys.stderr.write(f"\n=== current keys ({len(self.current)}) ===\n")
        # for k in self.current:
        #     sys.stderr.write(f"  {k}\n")
        # sys.stderr.flush()
        for key,cur in self.current.items():
            base=self.baseline.get(key)
            if base is None:
                print(f"[DEBUG] 无基线记录，跳过: {key}")
                continue#若是新增测试，不算漂移
            #从pass变为failed
            #print(f"[DEBUG] 匹配: {key} | base={base['status']} → cur={cur['status']}")
            if base["status"]=="passed" and cur["status"]=="failed":
                #print(f"[DEBUG] → 检测到 status_regression")
                self.drifts.append(
                    {
                        "key":key,
                        "type":"status_regression",
                        "baseline":base,
                        "current":cur,
                        "message":f"断言从pass变为faild"
                    }
                )
                continue
            #分数下降超过阈值
            base_score=base["score"]
            cur_score=cur["score"]
            if base_score >0 and (base_score-cur_score)/base_score>SCORE_DROP_THRESHOLD:
                #print(f"[DEBUG] → 检测到 score_drop")
                self.drifts.append(
                    {
                        "key": key,
                        "type": "score_drop",
                        "baseline": base,
                        "current": cur,
                        "message": (f"断言分数从{base_score:.4f}下降到{cur_score:.4f}"
                                    f"下降了{(base_score-cur_score)/base_score*100:.1f}%"
                                    )
                    }
                )
        return self.drifts

    def report(self)->str:
        if not self.drifts:
            return "\n[llm-assert] 基线对比通过，无行为漂移。\n"

        lines=[
            "",
            "="*60,
            f"[llm-assert]检测到{len(self.drifts)}处漂移",
            "="*60,
        ]
        for d in self.drifts:
            lines.append(f"\n[{d['type']}] {d['key']}")
            lines.append(f"  基线：score={d['baseline']['score']}"
                         f"| status:{d['baseline']['status']}"
                         )
            lines.append(f"  当前：score={d['current']['score']}"
                         f"| status:{d['current']['status']}"
                         )
            lines.append(f"  说明：{d['message']}")
        lines.append("="*60)
        return  "\n".join(lines)