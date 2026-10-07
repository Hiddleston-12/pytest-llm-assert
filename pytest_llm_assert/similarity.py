from sentence_transformers import SentenceTransformer, util
from pathlib import Path
model_path = Path(__file__).parent.parent/ "models" / "paraphrase-multilingual-MiniLM-L12-v2"
_model = SentenceTransformer(str(model_path))


def _get_model():
    """懒加载模型，只在第一次调用时下载和加载。"""
    global _model
    if _model is None:
        print("模型加载中")
        # all-MiniLM-L6-v2 只有约 80MB，CPU 就能跑，适合 CI
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model


def semantic_similarity(text1: str, text2: str) -> float:
    """返回两个句子的语义相似度，范围 0 到 1。"""
    if not text1 or not text2:
        return 0.0

    model = _get_model()
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)

    # cos_sim 返回 -1 到 1，我们映射到 0 到 1，方便理解
    raw = util.cos_sim(emb1, emb2).item()
    return (raw + 1) / 2