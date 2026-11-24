# NLP DocAI Retrieval

A research-oriented NLP and document-understanding project studying whether document layout information improves question answering and evidence retrieval compared with text-only methods.

## Research Question

> Does incorporating document layout information improve document question answering and evidence retrieval compared with text-only retrieval?

## Dataset

This project uses the **DocVQA Single Page Document Visual Question Answering** dataset.

The dataset includes document images, questions, answers, OCR text, word- and line-level coordinates, document IDs, and question types.

Official sources:

- [DocVQA Dataset](https://www.docvqa.org/datasets/docvqa)
- [RRC Download Portal](https://rrc.cvc.uab.es/?ch=17)

The project uses Task 1: **Single Page Document Visual Question Answering**.

Approximate verified dataset size:

| Partition | Questions | Documents | Images | Answers |
|---|---:|---:|---:|---|
| Training | 39,463 | 10,194 | 10,194 | Available |
| Validation | 5,349 | 1,286 | 1,286 | Available |
| Test | 5,188 | 1,287 | 1,287 | Not available locally |

Raw images, OCR files, and annotation archives are stored locally and are not committed to this repository.

## Task

Given a document page and a question, the system ranks OCR lines that may contain the answer.

Depending on the method, inputs include:

- The question
- OCR text
- OCR line or word coordinates
- The document image

Reference answers are used only for training labels and evaluation.

## Methods

### BM25 Baseline

`BM25-LINE` ranks OCR lines using text similarity between the question and OCR text. Coordinates are not used for ranking.

### Text-Only LightGBM

`LGBM-TEXT` is a supervised LightGBM reranker using text features such as BM25 scores, matching terms, line length, and question-line overlap.

### Layout-Aware LightGBM

`LGBM-LAYOUT` uses the text features above together with layout features such as:

- Horizontal and vertical position
- Line width and height
- Relative line order
- Bounding-box information

This is the proposed method.

### Shuffled-Layout Ablation

`LGBM-LAYOUT-SHUFFLED` changes or shuffles layout information while keeping the rest of the pipeline fixed. This tests whether meaningful spatial information contributes to performance.

### Qwen Visual Baseline

`QWEN-VISION` uses a pretrained visual document-question-answering model that receives a document image and question and generates an answer.

Qwen is evaluated separately because it generates answers, while BM25 and LightGBM rank OCR evidence lines.

## Evaluation Protocol

The official split manifest is:

```text
splits/docvqa_official_split.json
```

Because official test answers are unavailable locally, the labeled validation partition is divided into:

```text
Development: 2,641 questions
Internal held-out evaluation: 2,708 questions
```

The internal split is stored at:

```text
splits/val_dev_test_split.json
```

This internal held-out split is not the official DocVQA test set.

All retrieval methods use the same document pages, questions, OCR lines, preprocessing rules, answer normalization, and evaluation metrics.

Primary retrieval metrics:

- Evidence Recall@1
- Evidence Recall@5
- Evidence Recall@10
- Mean Reciprocal Rank

The Qwen baseline uses answer-level metrics such as Exact Match and ANLS.

## Training and Evaluation Workflow

```text
QAS and OCR data
      ↓
OCR-line feature extraction
      ↓
Train text-only LightGBM
      ↓
Train layout-aware LightGBM
      ↓
Evaluate on held-out data
      ↓
Compare metrics and analyze errors
```

Important scripts:

```text
src/bm25_line_baseline.py
src/build_line_features.py
src/train_lgbm_reranker.py
src/evaluate_line_ranker.py
```

Large derived feature files may be stored in Google Drive for Colab training and regenerated using the feature-extraction script.

## Error Analysis

The project analyzes:

- Tables
- Forms
- Multi-column pages
- Dense text
- Dates and numbers
- OCR errors
- Repeated answers
- Cases where layout helps or fails

Saved predictions are stored in:

```text
results/eval/
```

## Future Experiments

Future experiments may:

- Compare performance across document types
- Test different OCR-line and region-grouping strategies
- Measure robustness to OCR errors
- Compare original, removed, and shuffled coordinates
- Test generalization on another document dataset
- Add confidence or uncertainty estimation
- Compare LightGBM with document transformers

## Future Fine-Tuning Plan

A future extension will fine-tune a pretrained layout-aware transformer such as LayoutLMv3.

The planned process is:

1. Start with a pretrained document transformer.
2. Provide document images, OCR tokens, coordinates, and questions.
3. Fine-tune the model on the DocVQA training data.
4. Evaluate it using the same held-out protocol.
5. Compare it with BM25, LightGBM, and Qwen.
6. Remove or shuffle coordinates for a controlled ablation.

The transformer would be fine-tuned rather than trained from scratch. This extension may require GPU access and additional preprocessing.

## Reproducibility

The project records:

- Dataset and split versions
- Preprocessing settings
- Feature definitions
- Model configurations
- Random seeds
- Training and evaluation commands
- Predictions and metrics
- Hardware and runtime

Important files include:

```text
configs/
splits/
results/
evidence/EVIDENCE_RECORD.md
```

## Repository Structure

```text
nlp-docai-retrieval/
├── README.md
├── LICENSE
├── requirements.txt
├── configs/
├── data/
├── evidence/
├── figures/
├── notebooks/
├── paper/
├── results/
├── splits/
└── src/
```

## License and Dataset Usage

The source code is intended for academic and research purposes.

The DocVQA dataset is governed by the terms provided by the dataset organizers and the original document sources. Raw images, OCR files, annotation archives, and restricted download URLs must not be committed to or redistributed.

Users are responsible for reviewing and following the official dataset terms.

## Citation

```bibtex
@InProceedings{mathew2021docvqa,
    author = {Mathew, Minesh and Karatzas, Dimosthenis and Jawahar, C. V.},
    title = {DocVQA: A Dataset for VQA on Document Images},
    booktitle = {Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision},
    year = {2021}
}
```