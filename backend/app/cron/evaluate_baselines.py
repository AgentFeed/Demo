"""Offline comparison of ranking strategies on the same temporal validation split.

Strategies:
- popularity: ranks by the item popularity feature alone.
- hybrid-rules: the hand-weighted formula from 05_RECOMMENDATION_ENGINE.md.
- learned-logistic: the trained logistic ranker (backend/app/learning.py).

Usage:
    python -m app.cron.evaluate_baselines \
        --dataset training/simulated/interactions.csv \
        --users training/simulated/users.csv \
        --items training/simulated/items.csv \
        --report training/evaluation_report.md
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from app.learning import (
        LogisticRanker,
        example_features,
        evaluate_ranker,
        load_training_examples,
        temporal_split,
    )
else:
    from ..learning import (
        LogisticRanker,
        example_features,
        evaluate_ranker,
        load_training_examples,
        temporal_split,
    )


class PopularityRanker:
    label = "popularity"

    def predict(self, features: dict[str, float]) -> float:
        return features.get("popularity", 0.0)


class HybridRuleRanker:
    """The plan's hand-tuned weights; ignores learned parameters."""

    label = "hybrid-rules"
    weights = {
        "relevance": 0.35, "skill_overlap": 0.20, "social": 0.15,
        "freshness": 0.12, "popularity": 0.08, "eligibility": 0.10,
    }

    def predict(self, features: dict[str, float]) -> float:
        score = sum(weight * features.get(name, 0.0) for name, weight in self.weights.items())
        score -= 0.40 * features.get("hate", 0.0)
        score += 0.05 * features.get("referral", 0.0)
        return max(0.0, min(1.0, score))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare popularity, hybrid rules, and the learned ranker")
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--users", default=None)
    parser.add_argument("--items", default=None)
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--report", default=None, help="Optional markdown report path")
    args = parser.parse_args()

    examples = load_training_examples(args.dataset, users_path=args.users, items_path=args.items)
    train_examples, validation_examples = temporal_split(examples)
    if not validation_examples:
        raise SystemExit("Validation split is empty; need more rows.")

    # Overwrite the popularity feature with counts from the training period only,
    # so no strategy can see future popularity (temporal leakage).
    train_likes: Counter[str] = Counter()
    train_saves: Counter[str] = Counter()
    for row in train_examples:
        if row.action in {"view", "click", "like"}:
            train_likes[str(row.item_id)] += 1
        elif row.action == "save":
            train_saves[str(row.item_id)] += 1
    for row in examples:
        row.item["likes"] = train_likes.get(str(row.item_id), 0)
        row.item["saves"] = train_saves.get(str(row.item_id), 0)

    learned = LogisticRanker.empty().fit(train_examples, epochs=args.epochs)
    models: list[Any] = [PopularityRanker(), HybridRuleRanker(), learned]
    labels = ["popularity", "hybrid-rules", "learned-logistic"]
    results = {label: evaluate_ranker(model, validation_examples) for label, model in zip(labels, models)}
    payload = {
        "dataset": str(args.dataset),
        "trained_examples": len(train_examples),
        "validation_examples": len(validation_examples),
        "results": results,
        "note": "Same temporal validation split for all strategies; higher is better.",
    }
    print(json.dumps(payload, indent=2))

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Learned ranker evaluation report",
            "",
            f"- Dataset: `{payload['dataset']}`",
            f"- Train examples: {len(train_examples)} (earlier events)",
            f"- Validation examples: {len(validation_examples)} (later events, time-ordered split)",
            "",
            "| Strategy | NDCG@10 | Recall@10 | MRR |",
            "|---|---|---|---|",
        ]
        for label, metrics in results.items():
            lines.append(
                f"| {label} | {metrics['ndcg_at_10']:.4f} | {metrics['recall_at_10']:.4f} | {metrics['mrr']:.4f} |"
            )
        lines += [
            "",
            "All strategies are evaluated on the same temporal validation split.",
            "If the dataset is a simulation, these numbers demonstrate the pipeline only and must not be reported as real-world performance.",
            "",
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(json.dumps({"report": str(report_path)}))


if __name__ == "__main__":
    main()
