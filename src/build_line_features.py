import argparse
import json
import re
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi


def tokenize(text):
    return re.findall(r"[a-z0-9]+", str(text).lower())


def load_questions(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["data"] if isinstance(data, dict) else data


def normalize_box(box):
    """
    Converts OCR coordinates into:
    [x_min, y_min, x_max, y_max]
    """

    if not isinstance(box, list):
        return None

    if len(box) == 4:
        try:
            x1, y1, x2, y2 = [
                float(value)
                for value in box
            ]

            return [x1, y1, x2, y2]

        except (TypeError, ValueError):
            return None

    if len(box) >= 8:
        try:
            x_values = [
                float(box[index])
                for index in range(0, 8, 2)
            ]

            y_values = [
                float(box[index])
                for index in range(1, 8, 2)
            ]

            return [
                min(x_values),
                min(y_values),
                max(x_values),
                max(y_values)
            ]

        except (TypeError, ValueError):
            return None

    return None


def get_ocr_line_records(ocr_data):
    """
    Reads OCR lines and their bounding boxes.

    Supports the official DocVQA format:
    recognitionResults -> lines -> text/boundingBox

    Also supports:
    lines -> text/boundingBox
    """

    line_records = []

    if "recognitionResults" in ocr_data:
        results = ocr_data["recognitionResults"]

        if results:
            lines = results[0].get("lines", [])

            for line_number, line in enumerate(lines):
                text = line.get("text", "").strip()

                if not text:
                    continue

                raw_box = (
                    line.get("boundingBox")
                    or line.get("bbox")
                    or line.get("box")
                )

                line_records.append(
                    {
                        "line_number": line_number,
                        "text": text,
                        "bbox": normalize_box(raw_box)
                    }
                )

            return line_records

    if "lines" in ocr_data:
        for line_number, line in enumerate(ocr_data["lines"]):
            if not isinstance(line, dict):
                continue

            text = line.get("text", "").strip()

            if not text:
                continue

            raw_box = (
                line.get("boundingBox")
                or line.get("bbox")
                or line.get("box")
            )

            line_records.append(
                {
                    "line_number": line_number,
                    "text": text,
                    "bbox": normalize_box(raw_box)
                }
            )

    return line_records


def find_ocr_file(ocr_dir, image_name):
    image_stem = Path(image_name).stem

    direct_path = ocr_dir / f"{image_stem}.json"

    if direct_path.exists():
        return direct_path

    matches = list(
        ocr_dir.rglob(f"{image_stem}.json")
    )

    return matches[0] if matches else None


def answer_is_in_text(answers, text):
    text_tokens = tokenize(text)

    for answer in answers:
        answer_tokens = tokenize(answer)

        if not answer_tokens:
            continue

        answer_length = len(answer_tokens)

        for start in range(
            len(text_tokens) - answer_length + 1
        ):
            candidate_tokens = text_tokens[
                start:start + answer_length
            ]

            if candidate_tokens == answer_tokens:
                return True

    return False


def build_page_index(image_name, ocr_dir):
    ocr_file = find_ocr_file(
        ocr_dir,
        image_name
    )

    if ocr_file is None:
        raise FileNotFoundError(
            f"OCR file not found for image: {image_name}"
        )

    with open(ocr_file, "r", encoding="utf-8") as file:
        ocr_data = json.load(file)

    line_records = get_ocr_line_records(ocr_data)

    if not line_records:
        raise RuntimeError(
            f"No OCR lines found for image: {image_name}"
        )

    tokenized_lines = [
        tokenize(line["text"])
        for line in line_records
    ]

    bm25 = BM25Okapi(tokenized_lines)

    valid_boxes = [
        line["bbox"]
        for line in line_records
        if line["bbox"] is not None
    ]

    if valid_boxes:
        page_max_x = max(
            box[2]
            for box in valid_boxes
        )

        page_max_y = max(
            box[3]
            for box in valid_boxes
        )
    else:
        page_max_x = 1.0
        page_max_y = 1.0

    page_max_x = max(page_max_x, 1.0)
    page_max_y = max(page_max_y, 1.0)

    return {
        "lines": line_records,
        "bm25": bm25,
        "page_max_x": page_max_x,
        "page_max_y": page_max_y
    }


def calculate_features(
    question,
    line_record,
    bm25_score,
    page_index
):
    question_tokens = tokenize(question)
    line_tokens = tokenize(line_record["text"])

    question_token_set = set(question_tokens)
    line_token_set = set(line_tokens)

    matching_tokens = (
        question_token_set.intersection(line_token_set)
    )

    matching_token_count = len(matching_tokens)

    if len(question_token_set) > 0:
        overlap_ratio = (
            matching_token_count
            / len(question_token_set)
        )
    else:
        overlap_ratio = 0.0

    bbox = line_record["bbox"]

    if bbox is None:
        x_min = 0.0
        y_min = 0.0
        x_max = 0.0
        y_max = 0.0
        x_center_normalized = 0.0
        y_center_normalized = 0.0
        width_normalized = 0.0
        height_normalized = 0.0
        has_bbox = 0
    else:
        x_min, y_min, x_max, y_max = bbox

        page_max_x = page_index["page_max_x"]
        page_max_y = page_index["page_max_y"]

        width = max(x_max - x_min, 0.0)
        height = max(y_max - y_min, 0.0)

        x_center = (x_min + x_max) / 2.0
        y_center = (y_min + y_max) / 2.0

        x_center_normalized = (
            x_center / page_max_x
        )

        y_center_normalized = (
            y_center / page_max_y
        )

        width_normalized = (
            width / page_max_x
        )

        height_normalized = (
            height / page_max_y
        )

        has_bbox = 1

    total_lines = len(page_index["lines"])

    if total_lines > 1:
        line_position_normalized = (
            line_record["line_number"]
            / (total_lines - 1)
        )
    else:
        line_position_normalized = 0.0

    return {
        "bm25_score": float(bm25_score),
        "question_token_count": len(question_tokens),
        "line_token_count": len(line_tokens),
        "matching_token_count": matching_token_count,
        "overlap_ratio": overlap_ratio,
        "x_center_normalized": x_center_normalized,
        "y_center_normalized": y_center_normalized,
        "width_normalized": width_normalized,
        "height_normalized": height_normalized,
        "line_position_normalized": (
            line_position_normalized
        ),
        "has_bbox": has_bbox
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build text and layout features "
            "for DocVQA OCR lines"
        )
    )

    parser.add_argument(
        "--qas",
        required=True,
        help="Path to the QAS JSON file"
    )

    parser.add_argument(
        "--ocr-dir",
        required=True,
        help="Directory containing OCR JSON files"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Output CSV path"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of questions for a smoke test"
    )

    args = parser.parse_args()

    qas_path = Path(args.qas)
    ocr_dir = Path(args.ocr_dir)
    output_path = Path(args.output)

    questions = load_questions(qas_path)

    if args.limit is not None:
        questions = questions[:args.limit]

    print(f"Loaded questions: {len(questions)}")

    page_cache = {}
    feature_rows = []

    skipped_questions = 0
    positive_rows = 0

    for number, item in enumerate(
        questions,
        start=1
    ):
        question = item.get("question", "")
        image_name = item.get("image")
        answers = item.get("answers", [])

        if not question or not image_name:
            skipped_questions += 1
            continue

        if not isinstance(answers, list):
            answers = [answers]

        if image_name not in page_cache:
            try:
                page_cache[image_name] = build_page_index(
                    image_name=image_name,
                    ocr_dir=ocr_dir
                )
            except (FileNotFoundError, RuntimeError) as error:
                print(error)
                skipped_questions += 1
                continue

        page_index = page_cache[image_name]
        lines = page_index["lines"]
        bm25 = page_index["bm25"]

        question_scores = bm25.get_scores(
            tokenize(question)
        )

        for line_index, line_record in enumerate(lines):
            label = int(
                answer_is_in_text(
                    answers,
                    line_record["text"]
                )
            )

            if label == 1:
                positive_rows += 1

            features = calculate_features(
                question=question,
                line_record=line_record,
                bm25_score=question_scores[line_index],
                page_index=page_index
            )

            feature_rows.append(
                {
                    "question_id": item.get("questionId"),
                    "image": image_name,
                    "line_number": line_record["line_number"],
                    "text": line_record["text"],
                    "label": label,
                    **features
                }
            )

        if number % 100 == 0:
            print(
                f"Processed {number}/{len(questions)} questions"
            )

    if not feature_rows:
        raise RuntimeError(
            "No feature rows were created. "
            "Check the QAS and OCR paths."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe = pd.DataFrame(feature_rows)
    dataframe.to_csv(
        output_path,
        index=False
    )

    print("\nFeature extraction finished.")
    print(f"Rows created: {len(dataframe)}")
    print(f"Positive rows: {positive_rows}")
    print(f"Skipped questions: {skipped_questions}")
    print(f"Saved features to: {output_path}")
    print("\nFeature columns:")

    for column in dataframe.columns:
        print(f"  - {column}")


if __name__ == "__main__":
    main()