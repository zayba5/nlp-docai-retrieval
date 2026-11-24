# Evidence Record

## 1. Dataset Verification

**Dataset:** SP-DocVQA  
**Dataset version:** 1.0  
**Verification date:** October 31, 2026

The project uses the three official SP-DocVQA partitions.

| Partition | Questions | Documents | Images | Answers |
|---|---:|---:|---:|---|
| Training | 39,463 | 10,194 | 10,194 | Available |
| Validation | 5,349 | 1,286 | 1,286 | Available |
| Test | 5,188 | 1,287 | 1,287 | Not available locally |
| **Total** | **50,000** | **12,767** | **12,767** | — |

The complete dataset contains:

- 50,000 question records
- 12,767 unique document IDs
- 12,767 unique document-page images

Training and validation contain answer labels. The official test answers are not available locally, so answer-based evaluation cannot be performed on the official test partition.

The image counts can be added across partitions because the verification found zero overlapping images between the official partitions. The document counts can also be added because zero document overlap was found.

## 2. Relationship Between Dataset Files

The dataset consists of three connected components.

| Component | Location | Contents |
|---|---|---|
| Images | `data/raw/images/` | Original document-page images |
| OCR | `data/raw/ocr/` | Extracted text, words, lines, coordinates, and confidence values |
| QAS | `data/raw/qas/` | Questions, answers, image names, document IDs, and question types |

Each QAS record identifies a question, its answer, and the associated document image. The matching OCR file is located using the same base filename.

For example, a QAS record may contain:

- Question: What is the corporation name?
- Answer: USA Petroleum
- Image: `documents/ffbf0023_4.png`
- Document ID: `3278`

The corresponding local files are:

- Image: `data/raw/images/ffbf0023_4.png`
- OCR: `data/raw/ocr/ffbf0023_4.json`

The relationship between the files is:

- One document image is expected to have one OCR file with the same base filename.
- One document image can be referenced by multiple QAS records.
- Each QAS record connects a question and answer to a document image.
- The image and OCR files provide visual and machine-readable information about the same document page.
- The physical image-to-OCR correspondence should be verified separately from the QAS metadata.

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

The total number of questions is:

```text
39,463 + 5,349 + 5,188 = 50,000
```

The total number of unique images is:

```text
10,194 + 1,286 + 1,287 = 12,767
```

The total number of unique document IDs is:

```text
10,194 + 1,286 + 1,287 = 12,767
```

These totals are valid because the official partition checks found zero overlap between partitions.

### 2.3 Average Questions per Image

| Partition | Calculation | Average questions per image |
|---|---:|---:|
| Training | 39,463 / 10,194 | 3.87 |
| Validation | 5,349 / 1,286 | 4.16 |
| Test | 5,188 / 1,287 | 4.03 |
| **Complete dataset** | **50,000 / 12,767** | **3.92** |

These are averages. Individual document images may have one question or several questions.

## 3. Dataset Partition Organization

The images and OCR files remain in their original raw-data folders. They are not physically moved into separate training, validation, and test folders.

Instead, the QAS files determine the logical partition assignment.

| Partition | QAS source file | Questions | Documents | Images | Answers |
|---|---|---:|---:|---:|---|
| Training | `train_v1.0_withQT.json` | 39,463 | 10,194 | 10,194 | Available |
| Validation | `val_v1.0_withQT.json` | 5,349 | 1,286 | 1,286 | Available |
| Test | `test_v1.0.json` | 5,188 | 1,287 | 1,287 | Not available locally |

### 3.1 Partition Proportions

Question distribution:

| Partition | Percentage |
|---|---:|
| Training | 78.93% |
| Validation | 10.70% |
| Test | 10.38% |

Image distribution:

| Partition | Percentage |
|---|---:|
| Training | 79.85% |
| Validation | 10.07% |
| Test | 10.08% |

The difference between question and image percentages occurs because document images have different numbers of associated questions.

## 4. Partition Overlap Verification

The official partitions were checked for document and image overlap.

### Document overlap

| Partition comparison | Overlapping documents |
|---|---:|
| Training vs. Validation | 0 |
| Training vs. Test | 0 |
| Validation vs. Test | 0 |

### Image overlap

| Partition comparison | Overlapping images |
|---|---:|
| Training vs. Validation | 0 |
| Training vs. Test | 0 |
| Validation vs. Test | 0 |

No document-level or image-level overlap was identified between the official partitions. This helps prevent leakage caused by the same document appearing in multiple partitions.

## 5. OCR Inspection and Data Quality

The sample image `ffbf0023_4.png` was matched with its corresponding OCR file:

- Image: `data/raw/images/ffbf0023_4.png`
- OCR: `data/raw/ocr/ffbf0023_4.json`

The OCR file contained:

- 83 text lines
- Word-level OCR information
- Line-level OCR information
- Word-level and line-level bounding boxes
- OCR confidence values

Three associated questions were checked against the extracted OCR text.

| Result | Count |
|---|---:|
| Associated questions inspected | 3 |
| Answers found directly in OCR text | 2 |
| Answers not found through simple string matching | 1 |

The answers `Corporation` and `USA Petroleum` were found directly in the OCR text.

The date answer `7 - 1 - 99` was not found through simple string matching. Possible reasons include:

- Different spacing
- Different punctuation
- OCR recognition errors
- Different date formatting

This demonstrates that OCR extraction may not always accurately represent information visible in the original document.

## 6. Research Task

The project investigates the following question:

> Does incorporating document layout information improve evidence retrieval compared with text-only retrieval?

The system receives a question and the OCR information from its associated document page. It ranks OCR lines that may contain the answer.

The primary task is evidence retrieval rather than unrestricted answer generation.

## 7. Method Roster

| Method ID | Method | Inputs | Role |
|---|---|---|---|
| `BM25-LINE` | BM25 retrieval over OCR lines | Question and OCR text | Traditional text-only baseline |
| `LGBM-TEXT` | Text-only LightGBM reranker | Text and BM25 features | Ablation |
| `LGBM-LAYOUT` | Layout-aware LightGBM reranker | Text, BM25 features, and coordinates | Proposed method |
| `LGBM-LAYOUT-SHUFFLED` | Layout-aware model with shuffled layout information | Text and shuffled coordinates | Additional ablation |
| `QWEN-VISION` | Pretrained visual question-answering model | Document image and question | Visual comparison baseline |

## 8. Frozen Evaluation Protocol

The official split manifest is saved at:

```text
splits/docvqa_official_split.json
```

It records:

- Question IDs
- Document IDs
- Image filenames
- Source QAS files
- Partition assignments
- Partition counts

The original official partitions were checked for overlap and retained.

The corrected BM25 baseline uses OCR lines as its retrieval units rather than 80-word chunks. This gives more candidates per page and preserves the spatial identity of each line.

All retrieval methods use:

- The same document pages
- The same questions
- The same OCR-line candidates
- The same answer normalization procedure
- The same evaluation metrics
- The same information boundaries

## 9. Internal Development and Evaluation Split

Because the official DocVQA test answers are unavailable locally, the labeled official validation partition was divided into an internal development split and an internal held-out evaluation split.

| Internal partition | Questions | Purpose |
|---|---:|---|
| Development | 2,641 | Development and configuration decisions |
| Held-out evaluation | 2,708 | Final fixed comparison |
| Total | 5,349 | Complete official validation partition |

The internal split is saved at:

```text
splits/val_dev_test_split.json
```

The frozen experiment configuration is saved at:

```text
configs/frozen_config.json
```

The internal held-out evaluation split is not the official DocVQA test set.

Because the official validation partition was previously used for baseline development, the internal held-out split should not be interpreted as a completely untouched official test set. It is reported as an internal held-out evaluation split.

## 10. BM25 Chunk-Based Baseline

The original BM25 implementation divided each page into 80-word chunks with 20-word overlap.

| Setting | Value |
|---|---|
| Candidate unit | 80-word OCR chunks |
| Chunk overlap | 20 words |
| Questions evaluated | 5,349 |
| Unique pages | 1,286 |
| Total chunks | 4,517 |
| Average chunks per page | 3.51 |
| Coordinates used | No |

| Metric | Score | Percentage |
|---|---:|---:|
| Evidence Recall@1 | 0.6725 | 67.25% |
| Evidence Recall@5 | 0.8871 | 88.71% |
| Evidence Recall@10 | 0.8994 | 89.94% |

Because each page contained only approximately 3.5 chunks on average, Recall@5 and Recall@10 covered much of the page. These results are retained as a secondary historical reference.

## 11. BM25 Line-Based Baseline

To create a fair comparison with the layout-aware models, BM25 was rerun using OCR lines as candidate retrieval units.

Coordinates were saved but were not used by BM25 for ranking.

| Setting | Value |
|---|---|
| Baseline | `BM25-LINE` |
| Candidate unit | OCR line |
| Questions evaluated | 5,349 |
| Unique pages | 1,286 |
| Total OCR lines | 68,894 |
| Average lines per page | 53.57 |
| Coordinates saved | Yes |
| Coordinates used for ranking | No |
| Search scope | Question-associated page |

| Metric | Score | Percentage |
|---|---:|---:|
| Evidence Recall@1 | 0.1664 | 16.64% |
| Evidence Recall@5 | 0.3348 | 33.48% |
| Evidence Recall@10 | 0.4352 | 43.52% |

The result is stored at:

```text
results/bm25_line_validation.json
```

The lower scores compared with the original 80-word experiment are expected because individual OCR lines are smaller and more difficult to retrieve. The line-based results provide the fair comparison for the LightGBM models.

## 12. OCR Answer Coverage

The line-based BM25 evaluation found the normalized answer somewhere in the complete OCR text for:

```text
4,815 of 5,349 questions
```

The answer-in-OCR coverage was:

```text
4,815 / 5,349 = 90.02%
```

This represents an approximate upper bound for OCR-based evidence retrieval. If an answer is absent from the OCR, an OCR-only retrieval system cannot retrieve it.

OCR coverage is a data-quality measure, not a model-performance measure.

## 13. LightGBM Feature Extraction

To prepare the supervised models, each question was paired with the OCR lines from its associated document page.

The feature pipeline created:

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

An OCR line received label `1` if it contained a normalized reference answer and label `0` otherwise.

Reference answers were used to create training and evaluation labels, but were not included as model input features.

| Partition | Questions processed | Questions skipped | Feature rows | Positive rows |
|---|---:|---:|---:|---:|
| Training | 39,459 | 4 | 2,199,210 | 49,038 |
| Validation | 5,349 | 0 | 308,765 | 7,104 |

The four skipped training questions could not be converted into valid OCR-line feature records. This data-quality issue is documented and the remaining valid records were used for training.

The feature-generation script is:

```text
src/build_line_features.py
```

The generated feature files are:

```text
results/features/train_line_features.csv
results/features/validation_line_features.csv
```

The large training feature file may be stored separately in Google Drive or regenerated using the feature-generation command.

## 14. LightGBM Training Setup

The text-only LightGBM model uses:

- BM25 score
- Question token count
- OCR-line token count
- Matching token count
- Question-line overlap ratio

The layout-aware LightGBM model uses the text features above plus:

- Normalized horizontal position
- Normalized vertical position
- Normalized line width
- Normalized line height
- Normalized line-order position
- Bounding-box availability

The trained models are:

```text
results/models/lgbm_text.txt
results/models/lgbm_layout.txt
```

The corresponding metadata files are:

```text
results/models/lgbm_text_metadata.json
results/models/lgbm_layout_metadata.json
```

## 15. Development Results

The development results were used during experiment development.

| Method | Recall@1 | Recall@5 | Recall@10 | MRR | Questions |
|---|---:|---:|---:|---:|---:|
| BM25-LINE | 17.30% | 34.46% | 44.15% | 0.2679 | 2,641 |
| LGBM-LAYOUT-SHUFFLED | 15.15% | 32.11% | 44.04% | 0.2453 | 2,641 |
| LGBM-LAYOUT | 19.46% | 40.44% | 54.15% | 0.3020 | 2,641 |
| LGBM-TEXT | 19.31% | 36.77% | 48.43% | 0.2867 | 2,641 |

The development results are stored at:

```text
results/eval/dev_results_table.csv
```

## 16. Held-Out Evaluation Results

The held-out evaluation results were produced using the fixed internal evaluation split.

| Method | Recall@1 | Recall@5 | Recall@10 | MRR | Questions |
|---|---:|---:|---:|---:|---:|
| BM25-LINE | 15.99% | 32.53% | 42.91% | 0.2513 | 2,708 |
| LGBM-LAYOUT-SHUFFLED | 14.25% | 31.24% | 42.73% | 0.2345 | 2,708 |
| LGBM-LAYOUT | 17.95% | 38.07% | 51.11% | 0.2848 | 2,708 |
| LGBM-TEXT | 18.17% | 35.16% | 46.16% | 0.2729 | 2,708 |

The held-out results are stored at:

```text
results/eval/test_results_table.csv
```

The individual metric and prediction files are stored in:

```text
results/eval/
```

## 17. Result Interpretation

The layout-aware LightGBM model improved Recall@5, Recall@10, and MRR compared with the BM25-LINE baseline.

Compared with BM25-LINE, the layout-aware model improved:

- Recall@5 by approximately 5.54 percentage points
- Recall@10 by approximately 8.20 percentage points
- MRR by approximately 0.0335

Compared with the text-only LightGBM model, the layout-aware model improved:

- Recall@5 from 35.16% to 38.07%
- Recall@10 from 46.16% to 51.11%
- MRR from 0.2729 to 0.2848

The text-only LightGBM model had a slightly higher Recall@1 than the layout-aware model:

```text
LGBM-TEXT: 18.17%
LGBM-LAYOUT: 17.95%
```

Therefore, the benefit of layout information appears stronger for retrieving the correct evidence within the top five or top ten results than for selecting the single best result.

## 18. Ablation Analysis

The shuffled-layout ablation performed worse than the original layout-aware model on all reported metrics.

| Metric | LGBM-LAYOUT | Shuffled layout | Difference |
|---|---:|---:|---:|
| Recall@1 | 17.95% | 14.25% | +3.69 points |
| Recall@5 | 38.07% | 31.24% | +6.83 points |
| Recall@10 | 51.11% | 42.73% | +8.38 points |
| MRR | 0.2848 | 0.2345 | +0.0503 |

This supports the interpretation that meaningful spatial information contributes to retrieval performance. The improvement does not appear to result only from adding extra numeric features because shuffling the layout information reduced performance.

## 19. Qwen Visual Baseline

A pretrained `Qwen/Qwen2.5-VL-3B-Instruct` model was evaluated on a fixed 500-question subset.

The model received the document image and natural-language question. OCR text and OCR coordinates were not provided as direct model inputs.

| Setting | Value |
|---|---|
| Model | `Qwen/Qwen2.5-VL-3B-Instruct` |
| Dataset | SP-DocVQA |
| Evaluation subset | 500 questions |
| Random seed | 271 |
| Exact Match | 81.60% |
| Exactly correct predictions | 408 of 500 |
| ANLS | 86.91% |
| Metrics file | `results/visual_baseline/qwen_test_500_seed271_metrics.json` |
| Prediction file | `results/visual_baseline/qwen_test_500_seed271_checkpoint.json` |

The Qwen result is reported separately from BM25 and LightGBM because Qwen generates answers, while BM25 and LightGBM rank OCR evidence lines.

Therefore, Qwen Exact Match and ANLS are not directly comparable with Evidence Recall@1, Recall@5, Recall@10, or MRR.

The 500-question evaluation is treated as a visual-baseline subset of the internal held-out evaluation procedure. It is not reported as an official DocVQA test result.

## 20. Error Analysis

The saved top-ranked prediction files are located at:

```text
results/eval/
```

The error analysis will examine at least two concrete examples from categories such as:

- Tables
- Forms
- Dates and numbers
- Multi-column pages
- OCR errors
- Repeated answers

For each case, the analysis will record:

- Question
- Reference answer
- Question or document identifier
- Ranked evidence lines
- Method that succeeded or failed
- Likely explanation

This section must be completed after reviewing the saved prediction files.

## 21. Figures

The final paper will include two figures.

Figure 1 will compare BM25-LINE, LGBM-TEXT, and LGBM-LAYOUT using Recall@1, Recall@5, and Recall@10.

Figure 2 will show the layout ablation or an informative error slice, such as the difference between original and shuffled layout information.

The figure files and underlying values will be saved in:

```text
figures/
```

The figure-generation command will be documented in the README.

## 22. Reproducibility

The following files provide the configurations, splits, models, metrics, and predictions needed to reproduce the experiment:

```text
configs/frozen_config.json
splits/docvqa_official_split.json
splits/val_dev_test_split.json
results/models/
results/eval/
src/build_line_features.py
src/evaluate_line_ranker.py
```

The README will document:

- Environment installation
- Data-access instructions
- Feature-generation commands
- Model-training commands
- Evaluation commands
- Figure-generation commands
- Expected output locations

Large raw dataset files are not committed to the repository. They must be downloaded according to the official DocVQA terms.


## 23. Limitations

The results have several limitations:

- The internal held-out split was created from the official validation partition.
- The official DocVQA test answers are unavailable locally.
- Evidence retrieval is evaluated using answer-to-OCR matching rather than manually verified evidence regions.
- OCR errors can prevent correct retrieval.
- The Qwen evaluation uses 500 questions and is not directly comparable to the retrieval metrics.
- The results are limited to the SP-DocVQA dataset and the evaluated configurations.
- The findings do not establish universal superiority across all document types.

## 24. Summary

The project verified the SP-DocVQA dataset and its official partition separation. The corrected BM25-LINE baseline provides a text-only reference using OCR lines.

The LightGBM experiments compare a text-only model with a layout-aware model. On the internal held-out evaluation split, the layout-aware model improved Recall@5, Recall@10, and MRR compared with BM25 and the text-only LightGBM model. The shuffled-layout ablation performed worse, supporting the interpretation that meaningful layout information contributed to the improvement.

The conclusion is limited: layout information helped top-k evidence retrieval, but it did not improve Recall@1 over the text-only LightGBM model. Further analysis, figures, teammate reruns, and cross-team review documentation are required before final submission.

## 25. License and Dataset Usage

The source code in this repository is intended for academic and research purposes.

The DocVQA dataset is governed by the terms provided by the dataset organizers and the original document sources. The raw document images are provided for non-commercial research and educational use.

Raw images, OCR files, annotation archives, and restricted download URLs must not be committed to or redistributed through this repository. Users are responsible for reviewing and following the official dataset terms before downloading or using the data.

## 26. Citation

If you use the DocVQA dataset, please cite:

````bibtex
@InProceedings{mathew2021docvqa,
    author = {Mathew, Minesh and Karatzas, Dimosthenis and Jawahar, C. V.},
    title = {DocVQA: A Dataset for VQA on Document Images},
    booktitle = {Proceedings of the IEEE/CVF Winter Conference on Applications of Computer Vision},
    year = {2021}
}
````
