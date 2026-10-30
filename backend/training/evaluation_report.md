# Learned ranker evaluation report

- Dataset: `training/simulated/interactions.csv`
- Train examples: 15692 (earlier events)
- Validation examples: 3923 (later events, time-ordered split)

| Strategy | NDCG@10 | Recall@10 | MRR |
|---|---|---|---|
| popularity | 0.4397 | 0.7556 | 0.3639 |
| hybrid-rules | 0.4868 | 0.7742 | 0.4209 |
| learned-logistic | 0.4871 | 0.7701 | 0.4202 |

All strategies are evaluated on the same temporal validation split.
If the dataset is a simulation, these numbers demonstrate the pipeline only and must not be reported as real-world performance.
