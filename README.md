# Chinese–English Code-Switching in Hong Kong Café Reviews (CPC353 Assignment 1)

Dataset, annotation rules and analysis script for the CPC353 (Universiti Sains Malaysia, 2026/2027) group report
"Chinese–English Code-Switching in Hong Kong Café Reviews: A Frequency, N-gram and Concordance Analysis"
by Xiang Wentao, Ma Bowen and Zhu Yuedong.

## Contents

| Path | Description |
|---|---|
| `data/hk_cafe_reviews_121.csv` | 121 real customer reviews of Hong Kong cafés from foodpanda Hong Kong store review pages, with language label and switching type |
| `data/english_word_freq.csv` | English content words in the 46 code-switched reviews, with frequency and semantic domain |
| `data/chinese_word_freq.csv` | Chinese/Cantonese content words in the 46 code-switched reviews |
| `data/cross_language_bigrams.csv` | Token pairs across each language switch point (EN→ZH, ZH→EN) |
| `data/concordance_kwic.csv` | Keyword-in-context lines for frequent keywords (±35 characters) |
| `data/pilot_double_annotation_18.csv` | Independent double annotation of an 18-review pilot sample (17/18 agreement) |
| `data/audit_log_26.csv` | Source and label audit of 26 reviews |
| `analysis/analysis.py` | Preprocessing (OpenCC s2t, Han/Latin boundary splitting, jieba with a Cantonese dictionary), frequency, bigram and KWIC analysis |
| `docs/annotation_rules.md` | Annotation rules and recorded boundary decisions |

## Main columns of `hk_cafe_reviews_121.csv`

Review ID, Data Origin (all real), Product Category, Product (if stated), Source Platform, Source URL (store or chain review page;
individual review permalinks are not available), Rating (blank: not confirmed), Review Date, Review Text (original, unchanged),
Language Classification (Chinese / English / Code-switched / Other/uncertain), Code-Switching Type (Intra-sentential / Inter-sentential /
Tag Switching), Notes / Annotator Comments, Brand, Region, Branch, Collection date.

## Summary

- 121 reviews, 54 brands, 86 store review pages, review dates Apr 2025 – Oct 2026, collected 7 Nov 2026
- Chinese 41, English 34, Code-switched 46, Other/uncertain 0
- Switching type (per review): intra-sentential 45, tag 1, inter-sentential 0
- Written Cantonese is counted as Chinese. Brand names and complete menu item names alone do not count as switching.

## Notes on use

The reviews were collected by convenience sampling that deliberately sought mixed-language reviews, so language proportions
do not represent the platform. Review texts belong to their authors and the platform; this material is shared for academic,
non-commercial use in connection with the course report only. Reviewer names were not collected.

`analysis/analysis.py` was written in the analyst's local environment; its input and output paths must be adjusted before re-running.
