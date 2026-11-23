import argparse
import json
from pathlib import Path

import lightgbm as lgb
import pandas as pd


TEXT_FEATURES = [
    "bm25_score",
    "question_token_count",
    "line_token_count",
    "matching_token_count",
    "overlap_ratio",
]

LAYOUT_FEATURES = [
    "x_center_normalized",
    "y_center_normalized",
    "width_normalized",
    "height_normalized",
    "line_position_normalized",
    "has_bbox",
]


def load_training_data(path, feature_columns):
    required_columns = feature_columns + ["label"]

    dataframe = pd.read_csv(
        path,
        usecols=required_columns,
        dtype={
            feature: "float32"
            for feature in feature_columns
        }
        | {
            "label": "int8"
        },
    )

    dataframe = dataframe.dropna(
        subset=required_columns
    )

    features = dataframe[feature_columns]
    labels = dataframe["label"]

    return features, labels


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Train a LightGBM reranker using "
            "DocVQA OCR-line features."
        )
    )

    parser.add_argument(
        "--train-features",
        required=True,
        help="Path to the training feature CSV file.",
    )

    parser.add_argument(
        "--output-model",
        required=True,
        help="Path where the LightGBM model will be saved.",
    )

    parser.add_argument(
        "--output-metadata",
        required=True,
        help="Path where training metadata will be saved.",
    )

    parser.add_argument(
        "--feature-set",
        required=True,
        choices=["text", "layout"],
        help=(
            "Use text-only features or text plus "
            "layout features."
        ),
    )

    parser.add_argument(
        "--n-estimators",
        type=int,
        default=200,
        help="Number of boosting trees.",
    )

    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.05,
        help="Learning rate.",
    )

    parser.add_argument(
        "--num-leaves",
        type=int,
        default=31,
        help="Maximum number of leaves per tree.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=271,
        help="Random seed.",
    )

    args = parser.parse_args()

    if args.feature_set == "text":
        feature_columns = TEXT_FEATURES
        model_id = "LGBM-TEXT"

    else:
        feature_columns = (
            TEXT_FEATURES + LAYOUT_FEATURES
        )
        model_id = "LGBM-LAYOUT"

    print(f"Loading training data from: {args.train_features}")
    print(f"Feature set: {args.feature_set}")
    print(f"Model ID: {model_id}")

    features, labels = load_training_data(
        args.train_features,
        feature_columns,
    )

    positive_count = int((labels == 1).sum())
    negative_count = int((labels == 0).sum())

    if positive_count == 0:
        raise RuntimeError(
            "No positive training examples were found."
        )

    if negative_count == 0:
        raise RuntimeError(
            "No negative training examples were found."
        )

    scale_pos_weight = (
        negative_count / positive_count
    )

    print(f"Training rows: {len(features)}")
    print(f"Positive rows: {positive_count}")
    print(f"Negative rows: {negative_count}")
    print(
        "Positive-class weight: "
        f"{scale_pos_weight:.4f}"
    )

    model = lgb.LGBMClassifier(
        objective="binary",
        n_estimators=args.n_estimators,
        learning_rate=args.learning_rate,
        num_leaves=args.num_leaves,
        max_depth=-1,
        min_child_samples=20,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_lambda=1.0,
        scale_pos_weight=scale_pos_weight,
        random_state=args.seed,
        n_jobs=-1,
        verbosity=-1,
    )

    print("Training LightGBM...")

    model.fit(
        features,
        labels,
        feature_name=feature_columns,
    )

    model_path = Path(args.output_model)
    metadata_path = Path(args.output_metadata)

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    metadata_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    model.booster_.save_model(
        str(model_path)
    )

    metadata = {
        "model_id": model_id,
        "feature_set": args.feature_set,
        "feature_columns": feature_columns,
        "training_feature_file": str(
            args.train_features
        ),
        "num_training_rows": len(features),
        "positive_rows": positive_count,
        "negative_rows": negative_count,
        "scale_pos_weight": scale_pos_weight,
        "random_seed": args.seed,
        "parameters": {
            "objective": "binary",
            "n_estimators": args.n_estimators,
            "learning_rate": args.learning_rate,
            "num_leaves": args.num_leaves,
            "max_depth": -1,
            "min_child_samples": 20,
            "subsample": 0.9,
            "colsample_bytree": 0.9,
            "reg_lambda": 1.0,
        },
    }

    with open(
        metadata_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )

    print("\nTraining finished.")
    print(f"Saved model to: {model_path}")
    print(f"Saved metadata to: {metadata_path}")

    print("\nFeature importance:")

    importance_values = (
        model.feature_importances_
    )

    importance = sorted(
        zip(
            feature_columns,
            importance_values,
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    for feature_name, value in importance:
        print(f"  {feature_name}: {value}")


if __name__ == "__main__":
    main()