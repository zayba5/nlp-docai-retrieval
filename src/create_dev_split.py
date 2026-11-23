import argparse,json,random
import pandas as pd
ap=argparse.ArgumentParser()
ap.add_argument("--features", required=True)
ap.add_argument("--output", required=True)
ap.add_argument("--seed", type=int, default=271)
ap.add_argument("--dev-fraction", type=float, default=0.5)
a = ap.parse_args()

q = pd.read_csv(a.features, usecols=["question_id", "image"]).drop_duplicates("question_id")
images = sorted(q["image"].unique())
random.Random(a.seed).shuffle(images)
dev_images = set(images[: round(len(images) * a.dev_fraction)])

parts = {}
for name, mask in [("dev", q["image"].isin(dev_images)), ("test", ~q["image"].isin(dev_images))]:
    sub = q[mask]
    parts[name] = {"question_count": len(sub), "image_count": int(sub["image"].nunique()),
                   "question_ids": sorted(int(x) for x in sub["question_id"]),
                   "images": sorted(sub["image"].unique().tolist())}

assert not set(parts["dev"]["images"]) & set(parts["test"]["images"]), "image overlap"
json.dump({"source": "SP-DocVQA official validation", "unit": "document image",
           "seed": a.seed, "dev_fraction": a.dev_fraction, **parts},
          open(a.output, "w"), indent=2)
for k in ("dev", "test"):
    print(f"{k}: {parts[k]['question_count']} questions, {parts[k]['image_count']} images")
