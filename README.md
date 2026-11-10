# Chinese–English Code-Switching in Hong Kong Café Reviews (CPC353 Assignment 1)

Dataset, annotation rules and analysis script for the CPC353 (Universiti Sains Malaysia, 2026/2027) group report
"Chinese–English Code-Switching in Hong Kong Café Reviews: A Frequency, N-gram and Concordance Analysis"
by Xiang Wentao, Ma Bowen and Zhu Yuedong.

Version: final, 10 Nov 2026.

## Contents

| Path | Description |
|---|---|
| `data/hk_cafe_reviews_121.csv` | 121 publicly posted customer reviews of Hong Kong cafés from foodpanda Hong Kong review pages, with language label and switching type |
| `data/english_word_freq.csv` | English content words in the 47 code-switched reviews, with frequency and semantic domain (74 tokens / 51 types) |
| `data/chinese_word_freq.csv` | Chinese/Cantonese content words in the 47 code-switched reviews (240 tokens / 184 types) |
| `data/cross_language_bigrams.csv` | Token pairs at each language switch point, counted within sentences only (89 tokens / 86 types) |
| `data/concordance_kwic.csv` | Keyword-in-context lines for 22 keywords (±35 characters) |
| `data/pilot_double_annotation_18.csv` | Independent double annotation of an 18-review pilot sample (17/18 agreement) |
| `analysis/analysis.py` | Preprocessing (OpenCC s2t, Han/Latin boundary splitting, jieba with a 99-entry Cantonese and food dictionary), frequency, sentence-bounded bigram and KWIC analysis |
| `docs/annotation_rules.md` | Annotation rules and recorded boundary decisions |

## Main columns of `hk_cafe_reviews_121.csv`

Review ID, Data Origin, Product Category, Product (if stated), Source Platform, Source URL (store or chain review page;
individual review permalinks are not available), Review Date, Review Text (original, unchanged),
Language Classification (Chinese / English / Code-switched / Other/uncertain), Code-Switching Type (Intra-sentential /
Inter-sentential / Tag Switching), Brand, Branch, Collection date.

## Summary

- 121 reviews, 54 brands, 86 source pages (77 storefront codes), review dates Apr 2025 – Oct 2026, collected 7 Nov 2026
- Code-switched 47 (38.8%), Chinese 40 (33.1%), English 34 (28.1%), Other/uncertain 0
- Switching type (per review, of 47): intra-sentential 46, tag 1, inter-sentential 0
- Written Cantonese is counted as Chinese. Brand names, shop names and merchant-specific product names alone do not count as switching; generic English category words (flat white, bagel, hojicha latte) do.
- A 26-record sample (21.5%) was manually audited for store identity, text integrity and labels; the remaining records were not individually re-verified.

## Reproducing the statistics

```
pip install jieba opencc-python-reimplemented
python analysis/analysis.py
```

The script reads `data/hk_cafe_reviews_121.csv` and writes its outputs to `analysis/reproduced_outputs/`.

## Notes on use

The reviews were collected by convenience sampling that deliberately sought mixed-language reviews, so language proportions
do not represent the platform. Review texts belong to their authors and the platform; this material is shared for academic,
non-commercial use in connection with the course report only. Reviewer names were not collected.
