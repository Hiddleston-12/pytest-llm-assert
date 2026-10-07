import sys
from .similarity import semantic_similarity
from .nli import check_entailment
from .tone import detect_tone
from .baseline import BaselineRecorder

class BehaviorAssertion:
    """封装对一段 AI 输出的行为断言。"""

    def __init__(self, output: str,recorder=None,test_name:str=""):
        import sys
        #sys.stderr.write(f"[DEBUG] BehaviorAssertion.__init__: recorder={recorder is not None}\n")
        self._output = output
        self._recorder=recorder
        self._test_name=test_name

    def _record(self,assertion:str,target:str,score:float,status:str):
        #sys.stderr.write(f"[DEBUG] _record 被调用: {assertion} | recorder={self._recorder is not None}\n")
        #sys.stderr.flush()
        if self._recorder is not None:
            self._recorder.record(
                test_name=self._test_name,
                assertion=assertion,
                target=target,
                score=score,
                status=status,
            )

    def mentions(self, target: str, threshold: float = 0.5):
        """断言输出在语义上提到了 target。"""
        score = semantic_similarity(self._output, target)
        status="passed" if score>=threshold else "failed"
        self._record("mentions",target,score,status)
        if score < threshold:
            raise AssertionError(
                f"\n[llm-assert] mentions 断言失败\n"
                f"  目标短语 : {target}\n"
                f"  实际输出 : {self._output}\n"
                f"  相似度   : {score:.3f}（阈值 {threshold}）\n"
            )

        return self

    def not_mentions(self, target: str, threshold: float = 0.6):
        """断言输出在语义上没有提到 target。"""
        score = semantic_similarity(self._output, target)
        status = "passed" if score < threshold else "failed"
        normalized_score=1-score
        self._record("not_mentions", target, normalized_score, status)
        if score >= threshold:
            raise AssertionError(
                f"\n[llm-assert] mentions 断言失败\n"
                f"  目标短语 : {target}\n"
                f"  实际输出 : {self._output}\n"
                f"  相似度   : {score:.3f}（阈值 {threshold}）\n"
            )

        return self

    def grounded_in(self, context: str, threshold: float = 0.4):
        """断言输出是否有在上下文中提到，未提到则为幻觉
        判断逻辑：
        -ENTAILMENT 且分数大于=threshold ->pass
        -otherwise  ->fail
        """
        result = check_entailment(context, self._output)
        label = result["label"]
        score = result["score"]


        if label == "ENTAILMENT" :
            status = "passed" if score >= threshold else "failed"
            record_score=score
        else:
            status="failed"
            record_score=0.0

        self._record("grounded_in", context[:30], record_score, status)
        if status=="failed":
            raise AssertionError(
                f"\n[llm-assert] grounded_in 断言失败（疑似幻觉）\n"
                f"  上下文 : {context}\n"
                f"  输出   : {self._output}\n"
                f"  NLI 判断 : {label}（分数 {score:.4f}，阈值 {threshold}）\n"
                f"  说明   : 输出没有被上下文蕴含，可能编造了内容\n"
            )

        return self

    def tone(self, expected_tone: str, threshold: float = 0.5):
            result = detect_tone(self._output, threshold)
            actual_tone = result["tone"]
            score = result["score"]
            best_template = result.get("best_template")

            if actual_tone == expected_tone and score >= threshold:
                status="passed"
                record_score=score

            else:
                status="failed"
                record_score=0.0

            self._record("tone", expected_tone, record_score, status)

            if status=="failed":
                score_lines = "\n".join(
                    f"    {tone}: {s:.4f}"
                    for tone, s in sorted(
                        result["all_scores"].items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                )

                template_line = (
                    f"  命中模板 : {best_template}\n"
                    if best_template else ""
                )

                raise AssertionError(
                    f"\n[llm-assert] tone 断言失败\n"
                    f"  期望语气 : {expected_tone}\n"
                    f"  实际语气 : {actual_tone}（相似度 {score:.4f}，阈值 {threshold}）\n"
                    f"  实际输出 : {self._output}\n"
                    f"{template_line}"
                    f"  各语气得分:\n{score_lines}\n"
                )
            return self


def assert_behavior(output: str,recorder=None,test_name:str="") -> BehaviorAssertion:
    """入口函数：assert_behavior(ai_output).mentions('退款政策')"""
    #sys.stderr.write(f"[DEBUG] assert_behavior 被调用: recorder={recorder is not None}, test_name={test_name}\n")
    #sys.stderr.flush()
    if not isinstance(output, str):
        raise TypeError(
            f"assert_behavior 需要字符串，收到 {type(output).__name__}"
        )
    if not output.strip():
        raise ValueError("assert_behavior 收到空输出")

    return BehaviorAssertion(output,recorder,test_name)