"""Evaluate BM25-LINE, LGBM-TEXT, LGBM-LAYOUT and the shuffled-coordinate ablation on dev or test."""
import argparse, json, datetime
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb

LAYOUT_FEATURES = ["x_center_normalized", "y_center_normalized", "width_normalized",
                   "height_normalized", "line_position_normalized", "has_bbox"]


def score_metrics(df, ks=(1, 5, 10)):
    df = df.sort_values(["question_id", "score", "line_number"], ascending=[True, False, True])
    df["rank"] = df.groupby("question_id").cumcount() + 1
    first = df[df["label"] == 1].groupby("question_id")["rank"].min()
    n = df["question_id"].nunique()
    out = {f"Recall@{k}": float((first <= k).sum() / n) for k in ks}
    out["MRR"] = float((1.0 / first).sum() / n)
    out["num_questions"] = int(n)
    out["questions_with_positive_line"] = int(first.size)
    return out, df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=["bm25", "model"], required=True)
    ap.add_argument("--model-path")
    ap.add_argument("--metadata")
    ap.add_argument("--features", required=True)
    ap.add_argument("--split", required=True)
    ap.add_argument("--part", choices=["dev", "test"], required=True)
    ap.add_argument("--shuffle-layout", action="store_true")
    ap.add_argument("--seed", type=int, default=271)
    ap.add_argument("--output-dir", default="results/eval")
    a = ap.parse_args()

    ids = set(json.load(open(a.split))[a.part]["question_ids"])
    df = pd.read_csv(a.features)
    df = df[df["question_id"].isin(ids)].copy()

    if a.method == "bm25":
        method_id = "BM25-LINE"
        df["score"] = df["bm25_score"]
    else:
        meta = json.load(open(a.metadata))
        feats = meta["feature_columns"]
        method_id = meta["model_id"]
        if a.shuffle_layout:
            cols = [c for c in LAYOUT_FEATURES if c in feats]
            if not cols:
                raise SystemExit("--shuffle-layout needs the LGBM-LAYOUT model")
            rng = np.random.default_rng(a.seed)
            for idx in df.groupby("question_id").indices.values():
                rows = df.index[idx]
                df.loc[rows, cols] = df.loc[rng.permutation(rows), cols].to_numpy()
            method_id = "LGBM-LAYOUT-SHUFFLED"
        df["score"] = lgb.Booster(model_file=a.model_path).predict(df[feats].astype("float32"))

    metrics, ranked = score_metrics(df)
    run_id = f"{method_id}_{a.part}_{datetime.datetime.now():%Y%m%d_%H%M}"
    metrics.update(run_id=run_id, method_id=method_id, part=a.part, split_file=a.split,
                   model_path=a.model_path, shuffle_seed=a.seed if a.shuffle_layout else None)

    out = Path(a.output_dir); out.mkdir(parents=True, exist_ok=True)
    json.dump(metrics, open(out / f"{run_id}_metrics.json", "w"), indent=2)
    ranked[ranked["rank"] <= 10][["question_id", "rank", "line_number", "text", "score", "label"]] \
        .to_csv(out / f"{run_id}_top10.csv", index=False)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
