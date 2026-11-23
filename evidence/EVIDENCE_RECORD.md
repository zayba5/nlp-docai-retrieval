# Evidence Record

## 1. Dataset Verification

**Dataset:** SP-DocVQA  
**Dataset Version:** 1.0  
**Verification Date:** October 31, 2026

The project uses the three official SP-DocVQA partitions for baseline development, validation, and evaluation.

| Partition | Questions | Documents | Images | Answers |
|---|---:|---:|---:|---|
| Training | 39,463 | 10,194 | 10,194 | Available |
| Validation | 5,349 | 1,286 | 1,286 | Available |
| Test | 5,188 | 1,287 | 1,287 | Not included |
| **Total** | **50,000** | **12,767** | **12,767** | — |

The complete dataset contains:
- 50,000 question records.
- 12,767 unique document IDs.
- 12,767 unique document-page images.

Training and validation contain answer labels. Test answers are not available locally, so answer-based test evaluation cannot currently be performed.

## 2. Relationship Between Dataset Files

The dataset consists of three connected components:

| Component | Location | Contents |
|---|---|---|
| Images | `data/raw/images/` | Original document-page images |
| OCR | `data/raw/ocr/` | Extracted text, words, lines, coordinates, and confidence values |
| QAS | `data/raw/qas/` | Questions, answers, image names, document IDs, and question types |

Each QAS record identifies a question, its answer, and the associated document image. The matching OCR file is located using the same base filename.

For example, a QAS record contains:
- Question: What is the corporation name?
- Answer: USA Petroleum
- Image: `documents/ffbf0023_4.png`
- Document ID: `3278`

The corresponding local files are:
- Image: `data/raw/images/ffbf0023_4.png`
- OCR: `data/raw/ocr/ffbf0023_4.json`

The relationship between the files is:
- One document image corresponds to one expected OCR file.
- One document image can be referenced by multiple QAS question records.
- Each QAS record connects a question and its answer to the corresponding document image.
- The image and OCR files provide visual and machine-readable information about the same document page.

### 2.1 Question-to-Image Relationship

The dataset has a many-to-one relationship between questions and images. One document page can have several associated questions. Therefore, the number of questions is greater than the number of unique images.

For example, `ffbf0023_4.png` has three associated questions:

| Question ID | Question | Answer |
|---:|---|---|
| 9951 | When is the contract effective date? | `7 - 1 - 99` |
| 9952 | What is the type of organization? | `Corporation` |
| 9953 | What is the corporation name? | `USA Petroleum` |

All three questions reference the same image and OCR files:
- `data/raw/images/ffbf0023_4.png`
- `data/raw/ocr/ffbf0023_4.json`

This explains why the dataset contains 50,000 questions but only 12,767 unique images.

### 2.2 Count Calculations

The total number of questions is calculated by adding the three QAS partitions:

- Training: 39,463
- Validation: 5,349
- Test: 5,188

**Total questions:**

39,463 + 5,349 + 5,188 = **50,000**

The total number of unique images is calculated by adding the unique images in each partition:

- Training: 10,194
- Validation: 1,286
- Test: 1,287

**Total unique images:**

10,194 + 1,286 + 1,287 = **12,767**

The same calculation applies to the unique document IDs:

10,194 + 1,286 + 1,287 = **12,767 unique document IDs**

In the verified QAS metadata, the number of unique document IDs and unique image names is the same within each partition.

### 2.3 Average Questions per Image

The average number of questions per image is calculated by dividing the number of questions by the number of unique images.

| Partition | Calculation | Average Questions per Image |
|---|---|---:|
| Training | 39,463 / 10,194 | 3.87 |
| Validation | 5,349 / 1,286 | 4.16 |
| Test | 5,188 / 1,287 | 4.03 |
| **Complete Dataset** | **50,000 / 12,767** | **3.92** |

These values are averages. Individual images may have one question or several questions.

### 2.4 Image-to-OCR Relationship

Each document image is expected to have one corresponding OCR file with the same base filename.

For example:
- Image: `ffbf0023_4.png`
- OCR: `ffbf0023_4.json`

The expected relationship is one image to one OCR file.

Based on the QAS metadata, the expected total is approximately:
- 12,767 image files.
- 12,767 matching OCR files.

The physical image and OCR folder counts should be verified separately. These totals are based on unique image names and document IDs in the QAS metadata.

## 3. Dataset Partition Organization

The images and OCR files remain together in their original raw-data folders. They are not physically moved into separate training, validation, and test folders.

Instead, the QAS partition determines the logical assignment of each question and its associated document.

| Partition | QAS Source File | Questions | Unique Documents | Unique Images | Answers |
|---|---|---:|---:|---:|---|
| Training | `train_v1.0_withQT.json` | 39,463 | 10,194 | 10,194 | Available |
| Validation | `val_v1.0_withQT.json` | 5,349 | 1,286 | 1,286 | Available |
| Test | `test_v1.0.json` | 5,188 | 1,287 | 1,287 | Not included |
| **Total** | — | **50,000** | **12,767** | **12,767** | — |

### 3.1 Partition Proportions

The question distribution is:

| Partition | Percentage |
|---|---:|
| Training | 78.93% |
| Validation | 10.70% |
| Test | 10.38% |

The image distribution is:

| Partition | Percentage |
|---|---:|
| Training | 79.85% |
| Validation | 10.07% |
| Test | 10.08% |

The difference between question and image percentages occurs because different document images have different numbers of associated questions.

## 4. Partition Overlap Verification

The official partitions were checked for document and image overlap.

**Document overlap:**

| Partition Comparison | Overlapping Documents |
|---|---:|
| Training vs. Validation | 0 |
| Training vs. Test | 0 |
| Validation vs. Test | 0 |

**Image overlap:**

| Partition Comparison | Overlapping Images |
|---|---:|
| Training vs. Validation | 0 |
| Training vs. Test | 0 |
| Validation vs. Test | 0 |

No document-level or image-level overlap was identified between the three partitions.

This separation helps prevent data leakage caused by the same document appearing in multiple partitions.

## 5. OCR Inspection and Data Quality

The sample image `ffbf0023_4.png` was matched with its corresponding OCR file:

- Image: `data/raw/images/ffbf0023_4.png`
- OCR: `data/raw/ocr/ffbf0023_4.json`

The OCR file contained:
- 83 text lines.
- Word-level OCR information.
- Line-level OCR information.
- Word-level and line-level bounding boxes.
- OCR confidence values.

Three associated questions were checked against the extracted OCR text.

| Result | Count |
|---|---:|
| Associated questions inspected | 3 |
| Answers found directly in OCR text | 2 |
| Answers not found through simple string matching | 1 |

The answers `Corporation` and `USA Petroleum` were found directly in the OCR text.

The date answer `7 - 1 - 99` was not found through simple string matching. Possible reasons include:
- Differences in spacing.
- Different punctuation.
- OCR recognition errors.

This demonstrates that extracted OCR text may not always accurately represent information visible in the original document. This limitation is relevant to the project's comparison of text-based retrieval and layout-aware document question answering.

## 6. Baseline Evaluation Protocol

The project compares the following methods using the same fixed validation partition.

| Baseline | Purpose | Input |
|---|---|---|
| BM25 | Text-based retrieval baseline | OCR text and question |
| Visual baseline | Pretrained document question-answering comparison | Document image and question |
| Layout-aware method | Proposed approach investigating spatial information | OCR text, coordinates, and question |

The dataset partitions are used as follows:

- **Training:** Used for development and fitting learned components when required.
- **Validation:** Used for baseline comparison, development decisions, and model selection.
- **Test:** Reserved for final evaluation. Answer labels are not available locally.

All baseline methods will follow the same evaluation protocol and primary metric to ensure a fair comparison.

## 7. Frozen Evaluation Split

The project uses the official SP-DocVQA version 1.0 partitions:

- Training: `train_v1.0_withQT.json`
- Validation: `val_v1.0_withQT.json`
- Test: `test_v1.0.json`

The split manifest is saved at:

`splits/docvqa_official_split.json`

It records:
- Question IDs.
- Document IDs.
- Image filenames.
- Source QAS files.
- Partition assignments and counts.

The split is frozen to ensure consistent comparisons between baseline methods.

Raw images and OCR files are not moved or modified. Any necessary changes to the evaluation protocol will be documented, with the original version preserved and affected experiments rerun.

## 8. Reproducibility Evidence

The project package should contain:
- Runnable baseline source code or notebooks.
- Configuration and dependency information.
- Frozen split manifest.
- Baseline results and evaluation outputs.
- Runtime and hardware information.
- Teammate rerun results.

Each baseline result should record:
- Baseline and run IDs.
- Dataset and split version.
- Configuration and seed, where applicable.
- Evaluation count.
- Primary metric name and value.
- Runtime and hardware.
- Output file locations.

A teammate rerun should verify that the baselines can be executed using the provided instructions and produce consistent results.

## 9. Summary of Evidence

| Verification Item | Result |
|---|---|
| Dataset | SP-DocVQA v1.0 |
| Total questions | 50,000 |
| Unique document images | 12,767 |
| Unique document IDs | 12,767 |
| Training questions | 39,463 |
| Validation questions | 5,349 |
| Test questions | 5,188 |
| Training images | 10,194 |
| Validation images | 1,286 |
| Test images | 1,287 |
| Average questions per image | 3.92 |
| Expected image-to-OCR relationship | 1:1 |
| Document overlap | 0 |
| Image overlap | 0 |
| Sample OCR lines inspected | 83 |
| Sample questions inspected | 3 |
| Direct OCR answer matches | 2 |
| Unmatched OCR answers | 1 |
| Frozen split manifest | `splits/docvqa_official_split.json` |

## 10. Conclusion

The SP-DocVQA dataset provides the foundation for the project's baseline evaluation.

The dataset contains 50,000 questions associated with 12,767 unique document-page images, with an average of approximately 3.92 questions per image. Each image is expected to have one corresponding OCR file identified through its base filename.

The official training, validation, and test partitions were checked, with no document-level or image-level overlap identified.

The sample OCR inspection demonstrated that OCR extraction can introduce recognition and formatting errors. This limitation is relevant to the comparison between text-based retrieval and layout-aware document question answering.

These findings support proceeding with the BM25 and visual baselines before evaluating the proposed layout-aware method using the frozen evaluation protocol.

### BM25 Search Scope

Because this project uses the Single Page DocVQA task, each question is evaluated using the OCR text from its associated document page.

The BM25 baseline does not search OCR chunks from all validation pages at once. For every question, it loads the OCR file corresponding to that question's image and ranks only the chunks from that page.

This prevents the baseline from becoming a document-collection retrieval system and ensures that it matches the selected single-page question-answering task.

The BM25 baseline does not use OCR coordinates. It uses only OCR text, making it a text-only comparison for the future layout-aware method.

### Baseline Metric Scope

BM25 produces ranked OCR evidence chunks, so it is evaluated using Evidence Recall@1, Evidence Recall@5, and Evidence Recall@10.

The pretrained visual document-question-answering model produces predicted answers rather than ranked OCR evidence. It is therefore evaluated using answer-level metrics such as Exact Match and Token F1.

Evidence matching uses the answer text as a proxy because the dataset does not provide explicit evidence annotations for every question.

## BM25 Validation Results

The corrected BM25 baseline was evaluated on the complete DocVQA validation partition.

### Configuration

| Setting | Value |
|---|---|
| Baseline | BM25 text-only retrieval |
| Task | Single-Page DocVQA |
| Evaluation split | Validation |
| Questions loaded | 5,349 |
| Questions evaluated | 5,349 |
| Unique document pages | 1,286 |
| Total OCR chunks | 4,517 |
| Average chunks per page | 3.51 |
| Chunk size | 80 words |
| Chunk overlap | 20 words |
| Search scope | OCR chunks from the question-associated page |
| Coordinates used | No |
| Image pixels used | No |

### Results

| Metric | Score | Percentage |
|---|---:|---:|
| Evidence Recall@1 | 0.6725 | 67.25% |
| Evidence Recall@5 | 0.8871 | 88.71% |
| Evidence Recall@10 | 0.8994 | 89.94% |

### Interpretation

BM25 retrieved an OCR chunk containing the normalized answer for approximately 67.25% of validation questions within its first-ranked result.

When the top five retrieved chunks were considered, the evidence recall increased to approximately 88.71%.

When the top ten retrieved chunks were considered, the evidence recall increased slightly to approximately 89.94%.

This indicates that lexical similarity between the question and OCR text is often sufficient to locate answer-supporting text on the correct document page. However, the remaining failures suggest that text-only retrieval may struggle with OCR errors, tables, forms, repeated values, and relationships that depend on document layout.

The BM25 results provide the text-only reference point for the research question. The proposed layout-aware method will later be compared with these results to determine whether word positions, bounding boxes, and spatial relationships improve evidence retrieval.

### Evaluation Limitation

Evidence recall was estimated by checking whether a normalized answer string appeared in a retrieved OCR chunk. The dataset does not provide explicit evidence annotations for every question.

Therefore, this metric is an answer-to-OCR evidence proxy. It may count a chunk as successful when the answer appears but the chunk does not represent the true visual evidence region. It may also fail when OCR formatting differs from the provided answer.

The BM25 validation results are baseline results only. They do not establish whether layout improves performance because the layout-aware method has not yet been evaluated.

## Qwen Visual Baseline Results

A pretrained `Qwen/Qwen2.5-VL-3B-Instruct` model was evaluated on a fixed subset of 65 questions from the SP-DocVQA validation partition.

The model received only the document image and natural-language question. OCR text and OCR coordinates were not provided to the model.

| Setting | Value |
|---|---|
| Model | `Qwen/Qwen2.5-VL-3B-Instruct` |
| Task | Single-Page DocVQA |
| Evaluation subset | First 65 validation questions |
| Questions evaluated | 65 |
| Correct predictions | 49 |
| Incorrect predictions | 16 |
| Metric | Normalized Exact Match |
| Accuracy | 75.38% |
| Total runtime | 725.79 seconds |
| Average time per question | 11.17 seconds |
| Results file | `results/qwen_visual_65_questions.json` |
| Notebook | `notebooks/qwen_visual_baseline.ipynb` |
| Hardware | Google Colab GPU |

The Qwen accuracy was calculated as:

```text
49 correct predictions / 65 evaluated questions = 75.38%


## Line-Based BM25 Validation Results

To create a fair comparison for the proposed layout-aware method, the BM25 baseline was rerun using OCR lines as the retrieval candidates instead of 80-word chunks.

The line-based representation preserves smaller document regions and their bounding boxes. Coordinates were saved but were not used by BM25 for ranking.

| Setting | Value |
|---|---|
| Baseline | BM25-LINE |
| Evaluation split | SP-DocVQA validation |
| Questions evaluated | 5,349 |
| Unique document pages | 1,286 |
| Total OCR lines | 68,894 |
| Average lines per page | 53.57 |
| Candidate unit | OCR line |
| Coordinates saved | Yes |
| Coordinates used for ranking | No |
| Search scope | Question-associated page |
| Results file | `results/bm25_line_validation.json` |

| Metric | Score | Percentage |
|---|---:|---:|
| Evidence Recall@1 | 0.166386 | 16.64% |
| Evidence Recall@5 | 0.334829 | 33.48% |
| Evidence Recall@10 | 0.435222 | 43.52% |

### OCR Answer Coverage

The answer was found somewhere in the complete OCR text for 4,815 of 5,349 questions.

```text
4,815 / 5,349 = 90.02%

## LightGBM Feature Extraction

To prepare the proposed machine-learning models, the validation pages were represented as OCR-line candidates. Each question was paired with the OCR lines from its associated document page.

For every question-line pair, the pipeline created:

- Text similarity features
- Question-term overlap features
- Line-length features
- OCR bounding-box features
- Relative page-position features
- A binary answer-presence label

The answer label was used only to create supervised training targets. The answer itself was not included as an input feature.

### Feature Extraction Results

| Partition | Questions processed | Questions skipped | Feature rows | Positive rows |
|---|---:|---:|---:|---:|
| Training | 39,459 | 4 | 2,199,210 | 49,038 |
| Validation | 5,349 | 0 | 308,765 | 7,104 |

A positive row represents an OCR line containing a normalized reference answer. Multiple positive lines may occur for one question when the answer appears more than once.

The four skipped training questions were excluded because they could not be converted into valid OCR-line feature records. This data-quality issue will be documented and considered when interpreting the results.

### Feature Columns

The generated feature tables contain:

- BM25 score
- Question token count
- OCR-line token count
- Matching token count
- Question-line overlap ratio
- Normalized horizontal position
- Normalized vertical position
- Normalized line width
- Normalized line height
- Normalized line-order position
- Bounding-box availability
- Answer-presence label

The training feature table will be used to fit the LightGBM models. The validation feature table will be used only for evaluation.

The generated files are:

```text
results/features/train_line_features.csv
results/features/validation_line_features.csv

## Development / Protected Test Split (Assignment 3)

The official DocVQA test partition has no public answers, so the official validation partition was divided by document image into a development half (configuration selection) and a protected test half (final evaluation, run once).

| Item | Value |
|---|---|
| Script | `src/create_dev_split.py` |
| Output | `splits/val_dev_test_split.json` |
| Source | Official SP-DocVQA validation (5,349 questions, 1,286 images) |
| Split unit | Document image |
| Seed | 271 |
| Development | 2,641 questions, 643 images |
| Test (protected) | 2,708 questions, 643 images |
| Image overlap check | Passed (assertion in script, no shared images) |

Command:
```
python src/create_dev_split.py --features results/features/validation_line_features.csv --output splits/val_dev_test_split.json
```

## LightGBM Training

| Item | Value |
|---|---|
| Training file | `results/features/train_line_features.csv` (not committed; regenerate with `src/build_line_features.py`) |
| Training rows | 2,199,210 OCR lines |
| Positive rows | 49,038 |
| Skipped questions | 4 |
| Script | `src/train_lgbm_reranker.py` (binary objective, 200 trees, lr 0.05, 31 leaves, seed 271) |
| LGBM-TEXT | `results/models/lgbm_text.txt`, train time 42.1 s |
| LGBM-LAYOUT | `results/models/lgbm_layout.txt`, train time 24.1 s |
| Hardware | Local laptop CPU (TBD: model), Windows, Python venv; lightgbm 4.6.0 |
| Tuning | None; default hyperparameters from the training script |

Commands:
```
python src/build_line_features.py --qas data/raw/qas/train_v1.0_withQT.json --ocr-dir data/raw/ocr --output results/features/train_line_features.csv
python src/train_lgbm_reranker.py --train-features results/features/train_line_features.csv --output-model results/models/lgbm_text.txt --output-metadata results/models/lgbm_text_metadata.json --feature-set text
python src/train_lgbm_reranker.py --train-features results/features/train_line_features.csv --output-model results/models/lgbm_layout.txt --output-metadata results/models/lgbm_layout_metadata.json --feature-set layout
```

## Development Results (selection only, not final)

Split: development, N = 2,641. Higher is better.

| Method ID | Recall@1 | Recall@5 | Recall@10 | MRR | Run ID |
|---|---|---|---|---|---|
| BM25-LINE | 0.1730 | 0.3446 | 0.4415 | 0.2679 | BM25-LINE_dev_20261123_1402 |
| LGBM-TEXT | 0.1931 | 0.3677 | 0.4843 | 0.2867 | LGBM-TEXT_dev_20261123_1402 |
| LGBM-LAYOUT | 0.1946 | 0.4044 | 0.5415 | 0.3020 | LGBM-LAYOUT_dev_20261123_1402 |
| LGBM-LAYOUT-SHUFFLED | 0.1515 | 0.3211 | 0.4404 | 0.2453 | LGBM-LAYOUT-SHUFFLED_dev_20261123_1403 |

Saved: `results/eval/dev_results_table.csv` and per-run `*_metrics.json` / `*_top10.csv`.

## Configuration Freeze

| Item | Value |
|---|---|
| Record | `configs/frozen_config.json` |
| Frozen at | 2026-11-23 14:04:57 |
| Commit | `717e73c` (pushed before any test evaluation) |
| Fixed | Both models, split file, split seed 271, shuffle seed 271, metrics Recall@1/5/10 and MRR |

## Protected Test Results (final, run once)

Split: protected test, N = 2,708. Higher is better. Evaluated once after the freeze; commit `0dfcb65`.

| Method ID | Recall@1 | Recall@5 | Recall@10 | MRR | Run ID |
|---|---|---|---|---|---|
| BM25-LINE | 0.1599 | 0.3253 | 0.4291 | 0.2513 | BM25-LINE_test_20261123_1407 |
| LGBM-TEXT | 0.1817 | 0.3516 | 0.4616 | 0.2729 | LGBM-TEXT_test_20261123_1407 |
| LGBM-LAYOUT | 0.1795 | 0.3807 | 0.5111 | 0.2848 | LGBM-LAYOUT_test_20261123_1408 |
| LGBM-LAYOUT-SHUFFLED | 0.1425 | 0.3124 | 0.4273 | 0.2345 | LGBM-LAYOUT-SHUFFLED_test_20261123_1408 |

Saved: `results/eval/test_results_table.csv` and per-run `*_metrics.json` / `*_top10.csv`.

Evaluation command (change `--method`, model paths, `--part`, and add `--shuffle-layout` as listed in the README):
```
python src/evaluate_line_ranker.py --method model --model-path results/models/lgbm_layout.txt --metadata results/models/lgbm_layout_metadata.json --features results/features/validation_line_features.csv --split splits/val_dev_test_split.json --part test --output-dir results/eval
```

## Ablations (test split)

| Comparison | Changed component | Recall@5 full | Recall@5 ablated | Difference | MRR difference |
|---|---|---|---|---|---|
| LGBM-LAYOUT vs LGBM-TEXT | Layout features removed (same data, training, scoring) | 0.3807 | 0.3516 | -0.0291 | -0.0119 |
| LGBM-LAYOUT vs LGBM-LAYOUT-SHUFFLED | Same model; layout features permuted across lines within each question (seed 271) | 0.3807 | 0.3124 | -0.0683 | -0.0503 |

Note: Recall@1 is essentially tied between LGBM-LAYOUT (0.1795) and LGBM-TEXT (0.1817).
Line-level ceiling: questions with at least one answer-containing line (dev 2,328 / 2,641).
