from transformers import pipeline
from pathlib import Path
'''
测试nli模型是否正确加载+测试模型效果
'''
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"

# print("模型路径:", MODEL_PATH)
# print("路径存在:", MODEL_PATH.exists())
# print("目录内容:", list(MODEL_PATH.iterdir())[:5] if MODEL_PATH.exists() else "不存在")
nli = pipeline(
            "text-classification",
            model=str(MODEL_PATH),
            tokenizer=str(MODEL_PATH),
            local_files_only=True,   # 只用本地文件
        )
#nli = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-small")

premise = "We support 7-day no-reason refunds. However, for customized products, refund or exchange requests are only allowed due to quality issues. Refund requests must be submitted on the order page and will be processed within 3 business days."
hypothesis = "We offer a 7-day no-questions-asked refund policy. You can apply for a refund on the order page. We deeply apologize for not being able to meet your needs, and we fully understand how you feel."

# 新的正确写法
result = nli({"text": premise, "text_pair": hypothesis})
print(result)