import os
from pathlib import Path
from transformers import pipeline
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"
# 本地模型的实际路径
_nli = None


def _get_nli():
    """懒加载 NLI 模型，从本地路径加载，不联网。"""
    global _nli
    if _nli is None:
        print("模型加载中")
        _nli = pipeline(
            "text-classification",
            model=str(MODEL_PATH),
            tokenizer=str(MODEL_PATH),
            local_files_only=True,   # 只用本地文件
        )
    return _nli


LABEL_MAP = {
    "LABEL_0": "CONTRADICTION",
    "LABEL_1": "ENTAILMENT",
    "LABEL_2": "NEUTRAL",
    "contradiction": "CONTRADICTION",
    "entailment": "ENTAILMENT",
    "neutral": "NEUTRAL",
}


def check_entailment(premise: str, hypothesis: str) -> dict:
    if not premise or not hypothesis:
        return {"label": "NEUTRAL", "score": 0.0}

    nli = _get_nli()
    result = nli({"text": premise, "text_pair": hypothesis})

    label = LABEL_MAP.get(result["label"], result["label"])
    return {"label": label, "score": result["score"]}