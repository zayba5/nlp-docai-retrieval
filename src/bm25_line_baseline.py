import argparse
import json
import re
from pathlib import Path

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

    Supports the official format:
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

    page_lines = []

    for line_record in line_records:
        page_lines.append(
            {
                "image": image_name,
                "line_number": line_record["line_number"],
                "text": line_record["text"],
                "bbox": line_record["bbox"]
            }
        )

    tokenized_lines = [
        tokenize(line["text"])
        for line in page_lines
    ]

    bm25 = BM25Okapi(tokenized_lines)

    return page_lines, bm25


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Line-based BM25 baseline for "
            "Single-Page DocVQA"
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
        help="Path for the output JSON file"
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

    retrieval_k = [1, 5, 10]

    evidence_hits = {
        k: 0
        for k in retrieval_k
    }

    answer_coverage_hits = 0
    page_cache = {}
    predictions = []
    evaluated_questions = 0

    for number, item in enumerate(
        questions,
        start=1
    ):
        question = item.get("question", "")
        gold_image = item.get("image")
        answers = item.get("answers", [])

        if not question or not gold_image:
            raise ValueError(
                f"Question {number} is missing "
                "a question or image."
            )

        if not isinstance(answers, list):
            answers = [answers]

        if not answers:
            raise ValueError(
                f"Question {number} has no answer labels."
            )

        if gold_image not in page_cache:
            page_cache[gold_image] = build_page_index(
                image_name=gold_image,
                ocr_dir=ocr_dir
            )

        page_lines, bm25 = page_cache[gold_image]

        scores = bm25.get_scores(
            tokenize(question)
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True
        )

        ranked_lines = [
            {
                **page_lines[index],
                "bm25_score": float(scores[index])
            }
            for index in ranked_indices
        ]

        evaluated_questions += 1

        full_page_text = " ".join(
            line["text"]
            for line in page_lines
        )

        if answer_is_in_text(
            answers,
            full_page_text
        ):
            answer_coverage_hits += 1

        for k in retrieval_k:
            top_lines = ranked_lines[:k]

            evidence_found = any(
                answer_is_in_text(
                    answers,
                    line["text"]
                )
                for line in top_lines
            )

            if evidence_found:
                evidence_hits[k] += 1

        predictions.append(
            {
                "question_id": item.get("questionId"),
                "question": question,
                "gold_image": gold_image,
                "answers": answers,
                "num_candidate_lines": len(page_lines),
                "top_results": ranked_lines[:10]
            }
        )

        if number % 100 == 0:
            print(
                f"Processed {number}/{len(questions)} questions"
            )

    if evaluated_questions == 0:
        raise RuntimeError(
            "No questions were evaluated. "
            "Check the QAS and OCR paths."
        )

    total_candidate_lines = sum(
        len(page_lines)
        for page_lines, _ in page_cache.values()
    )

    average_lines_per_page = (
        total_candidate_lines / len(page_cache)
        if page_cache
        else 0.0
    )

    metrics = {
        "task": "single_page_docvqa",
        "baseline": "BM25-LINE",
        "search_scope": "question_associated_page",
        "candidate_unit": "ocr_line",
        "ocr_coordinates_saved": True,
        "ocr_coordinates_used_for_ranking": False,
        "num_questions_loaded": len(questions),
        "num_questions_evaluated": evaluated_questions,
        "num_unique_pages": len(page_cache),
        "num_total_candidate_lines": total_candidate_lines,
        "average_lines_per_page": average_lines_per_page,
        "answer_in_ocr_count": answer_coverage_hits,
        "answer_in_ocr_coverage": (
            answer_coverage_hits / evaluated_questions
        ),
        "evidence_recall": {
            f"Recall@{k}": (
                evidence_hits[k] / evaluated_questions
            )
            for k in retrieval_k
        }
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {
        "baseline": "BM25-LINE",
        "metrics": metrics,
        "predictions": predictions
    }

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("\nLine-based BM25 baseline finished.")
    print(json.dumps(metrics, indent=2))
    print(f"Saved results to: {output_path}")


if __name__ == "__main__":
    main()