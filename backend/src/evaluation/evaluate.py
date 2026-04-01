# src/evaluation/evaluate.py
import json
import argparse
import numpy as np
from pathlib import Path
from rouge_score import rouge_scorer
from bert_score import score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
from src.vectorstore.pinecone_store import similarity_search
from app.graph import build_graph

# ── Retrieval Metrics ───────────────────────────────
def precision_at_k(retrieved: list, relevant: list, k: int) -> float:
    retrieved_k = retrieved[:k]
    hits = sum(1 for doc in retrieved_k if doc in relevant)
    return hits / k if k > 0 else 0.0

def recall_at_k(retrieved: list, relevant: list, k: int) -> float:
    retrieved_k = retrieved[:k]
    hits = sum(1 for doc in retrieved_k if doc in relevant)
    return hits / len(relevant) if relevant else 0.0

def mean_reciprocal_rank(retrieved: list, relevant: list) -> float:
    for rank, doc in enumerate(retrieved, start=1):
        if doc in relevant:
            return 1.0 / rank
    return 0.0

# ── Generation Metrics ──────────────────────────────
def compute_bleu(predictions: list[str], references: list[str]) -> float:

    nltk.download("punkt", quiet=True)

    smoother = SmoothingFunction().method1
    scores = []
    for pred, ref in zip(predictions, references):
        pred_tokens = pred.lower().split()
        ref_tokens  = ref.lower().split()
        score = sentence_bleu([ref_tokens], pred_tokens, smoothing_function=smoother)
        scores.append(score)
    return np.mean(scores)

def compute_rouge(predictions: list[str], references: list[str]) -> dict:
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)

    scores = {"rouge1": [], "rouge2": [], "rougeL": []}
    for pred, ref in zip(predictions, references):
        result = scorer.score(ref, pred)
        scores["rouge1"].append(result["rouge1"].fmeasure)
        scores["rouge2"].append(result["rouge2"].fmeasure)
        scores["rougeL"].append(result["rougeL"].fmeasure)

    return {k: np.mean(v) for k, v in scores.items()}

def compute_bertscore(predictions: list[str], references: list[str]) -> float:
    P, R, F1 = score(predictions, references, lang="vi", verbose=False)
    return F1.mean().item()

# ── Retrieval Pipeline ──────────────────────────────
def retrieve_docs(query: str, k: int = 3) -> list[str]:
    docs = similarity_search(query, k=k)
    return [doc.id for doc in docs]

# ── Generate Answer ─────────────────────────────────
def generate_answer(query: str) -> str:
    """Generate answer using the full RAG pipeline."""
    graph = build_graph()
    result = graph.invoke({
        "query": query,
        "session_id": "eval",
        "iteration_count": 0
    })
    return result.get("answer", "")

# ── Main Evaluation ─────────────────────────────────
def evaluate(dataset_path: str, metrics: list[str], k: int = 3):
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"\n{'='*50}")
    print(f"  Evaluating on {len(dataset)} samples")
    print(f"  Metrics: {', '.join(metrics)}")
    print(f"{'='*50}\n")

    predictions, references = [], []
    precision_scores, recall_scores, mrr_scores = [], [], []

    for i, sample in enumerate(dataset):
        query        = sample["query"]
        reference    = sample["reference"]
        relevant_ids = sample.get("relevant_docs", [])

        print(f"[{i+1}/{len(dataset)}] Query: {query[:60]}...")

        # Retrieval evaluation
        if any(m in metrics for m in ["precision", "recall", "mrr"]):
            retrieved = retrieve_docs(query, k=k)
            if "precision" in metrics:
                precision_scores.append(precision_at_k(retrieved, relevant_ids, k))
            if "recall" in metrics:
                recall_scores.append(recall_at_k(retrieved, relevant_ids, k))
            if "mrr" in metrics:
                mrr_scores.append(mean_reciprocal_rank(retrieved, relevant_ids))

        # Generation evaluation
        if any(m in metrics for m in ["bleu", "rouge", "bertscore"]):
            answer = generate_answer(query)
            predictions.append(answer)
            references.append(reference)

    # ── Print Results ───────────────────────────────
    print(f"\n{'='*50}")
    print("  EVALUATION RESULTS")
    print(f"{'='*50}")

    if "precision" in metrics and precision_scores:
        print(f"  Precision@{k}   : {np.mean(precision_scores):.4f}")
    if "recall" in metrics and recall_scores:
        print(f"  Recall@{k}      : {np.mean(recall_scores):.4f}")
    if "mrr" in metrics and mrr_scores:
        print(f"  MRR            : {np.mean(mrr_scores):.4f}")

    if "bleu" in metrics and predictions:
        bleu = compute_bleu(predictions, references)
        print(f"  BLEU-4         : {bleu:.4f}")

    if "rouge" in metrics and predictions:
        rouge = compute_rouge(predictions, references)
        print(f"  ROUGE-1        : {rouge['rouge1']:.4f}")
        print(f"  ROUGE-2        : {rouge['rouge2']:.4f}")
        print(f"  ROUGE-L        : {rouge['rougeL']:.4f}")

    if "bertscore" in metrics and predictions:
        bert = compute_bertscore(predictions, references)
        print(f"  BERTScore (F1) : {bert:.4f}")

    print(f"{'='*50}\n")

    # ── Save Results ────────────────────────────────
    results = {
        "dataset": dataset_path,
        "num_samples": len(dataset),
        "k": k,
        "metrics": {}
    }

    if precision_scores: results["metrics"][f"precision@{k}"] = round(np.mean(precision_scores), 4)
    if recall_scores:    results["metrics"][f"recall@{k}"]    = round(np.mean(recall_scores), 4)
    if mrr_scores:       results["metrics"]["mrr"]             = round(np.mean(mrr_scores), 4)
    if predictions:
        if "bleu"      in metrics: results["metrics"]["bleu"]       = round(compute_bleu(predictions, references), 4)
        if "rouge"     in metrics: results["metrics"].update({f"rouge_{k}": round(v, 4) for k, v in compute_rouge(predictions, references).items()})
        if "bertscore" in metrics: results["metrics"]["bertscore"]  = round(compute_bertscore(predictions, references), 4)

    output_path = Path("data/eval/results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"  Results saved to {output_path}")

# ── CLI ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate RAG pipeline")
    parser.add_argument("--dataset",  type=str, default="data/eval/eval.json")
    parser.add_argument("--metrics",  type=str, nargs="+",
                        default=["precision", "recall", "mrr", "bleu", "rouge", "bertscore"])
    parser.add_argument("--k",        type=int, default=3)
    args = parser.parse_args()

    evaluate(
        dataset_path=args.dataset,
        metrics=args.metrics,
        k=args.k
    )