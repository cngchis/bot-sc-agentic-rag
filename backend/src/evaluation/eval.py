import json
import argparse
import time
import numpy as np
from pathlib import Path
from rouge_score import rouge_scorer
from bert_score import score
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import nltk
from app.graph import build_graph

graph = build_graph()

# Generation Metrics
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

# Generate Answer
def generate_answer(query: str) -> str:
    """Generate answer using the full RAG pipeline."""
    t0 = time.perf_counter()
    result = graph.invoke({
        "query": query,
        "session_id": "eval",
        "iteration_count": 0    
    })
    latency_ms = (time.perf_counter() - t0) * 1_000
    iteration_count = result.get("iteration_count", 0)
    
    return {
        "answer": result.get("answer", ""),
        "iteration_count": iteration_count,
        "latency_ms": latency_ms,
    }

# Main Evaluation Loop
def evaluate(dataset_path: str, metrics: list[str]):
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Evaluating on {len(dataset)} samples")
    print(f"Metrics: {', '.join(metrics)}")
    print()

    predictions, references, latencies_ms = [], [], []

    for i, sample in enumerate(dataset):
        query = sample["query"]
        reference = sample["reference"]

        print(f"[{i+1}/{len(dataset)}] Query: {query[:60]}...")

        # Generation evaluation
        gen = generate_answer(query)
        predictions.append(gen["answer"])
        references.append(reference)
        latencies_ms.append(gen["latency_ms"])
        print(f"  latency={gen['latency_ms']:.0f}ms, iterations={gen['iteration_count']}")

    print("EVALUATION RESULTS")

    # Print Results
    if "bleu" in metrics and predictions:
        bleu = compute_bleu(predictions, references)
        print(f"BLEU: {bleu:.4f}")

    if "rouge" in metrics and predictions:
        rouge = compute_rouge(predictions, references)
        print(f"ROUGE-1: {rouge['rouge1']:.4f}")
        print(f"ROUGE-2: {rouge['rouge2']:.4f}")
        print(f"ROUGE-L: {rouge['rougeL']:.4f}")

    if "bertscore" in metrics and predictions:
        bert = compute_bertscore(predictions, references)
        print(f"BERTScore (F1): {bert:.4f}")

    if latencies_ms:
        avg_latency = np.mean(latencies_ms)
        print(f"Average Latency: {avg_latency:.2f} ms")

    # Save results to JSON
    results = {
        "dataset": dataset_path,
        "num_samples": len(dataset),
        "metrics": {}
    }

    if predictions:
        if "bleu"      in metrics: results["metrics"]["bleu"]       = round(compute_bleu(predictions, references), 4)
        if "rouge"     in metrics: results["metrics"].update({f"rouge_{k}": round(v, 4) for k, v in compute_rouge(predictions, references).items()})
        if "bertscore" in metrics: results["metrics"]["bertscore"]  = round(compute_bertscore(predictions, references), 4)
        if "latency"   in metrics: results["metrics"]["avg_latency_ms"] = round(np.mean(latencies_ms), 2)

    output_path = Path("outputs/results.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Agentic RAG pipeline")
    parser.add_argument("--dataset",  type=str, default="data/json/eval.json")
    parser.add_argument("--metrics",  type=str, nargs="+",
                        default=["bleu", "rouge", "bertscore", "latency"])
    args = parser.parse_args()

    evaluate(
        dataset_path=args.dataset,
        metrics=args.metrics
    )