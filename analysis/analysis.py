# -*- coding: utf-8 -*-
"""
CPC353 Assignment 1 — Member B final reproducible pipeline (2026-11-10)
=======================================================================
Reads the delivered 121-record corpus (`03_最终核验121条语料全集.csv`) and
regenerates every derived table from scratch:

  06_混用评论英文高频词与语义分类表.csv   74 tokens / 51 types, 5 domains
  07_混用评论中文高频词表.csv             240 tokens / 184 types
  08_跨语言边界Bigram二元语法搭配表.csv    89 switching points / 86 types
  09_关键词KWIC语境全量数据库.csv          ±35-character concordance
  nlp_analysis_results_perfect.json        all headline statistics

Key rules encoded here
----------------------
1. Unified annotation rule: generic English category terms (flat white,
   bagel, dirty, allday breakfast, hojicha latte) count as code-switching;
   only brand / store / proprietary full names are excluded.
2. `begal` is kept as a surface variant but mapped to Western Bakery & Food.
3. `gym` is a leisure noun and gets its own Leisure & Activity domain.
4. Bigrams are computed WITHIN sentence boundaries only. Sentence-final
   punctuation: 。！？!?；;… and ASCII '.' not between digits. Commas do not
   break a bigram.
5. Four verified branch corrections are re-applied idempotently.

Usage
-----
    python 10_全流程可复现分析脚本_终极版.py
    python 10_全流程可复现分析脚本_终极版.py --in-place

Default output: ./reproduced_outputs/ ; --in-place writes beside the script.
"""
import csv
import json
import os
import re
import sys
from collections import Counter

import jieba
import opencc

sys.stdout.reconfigure(encoding="utf-8")

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "03_最终核验121条语料全集.csv")
if not os.path.exists(SRC):  # repository layout: analysis/ + data/
    SRC = os.path.join(BASE, "..", "data", "hk_cafe_reviews_121.csv")
OUT = BASE if "--in-place" in sys.argv else os.path.join(BASE, "reproduced_outputs")
os.makedirs(OUT, exist_ok=True)

if not os.path.exists(SRC):
    raise SystemExit(f"Cannot find corpus: {SRC}")

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
for _r in rows:  # the public CSV omits the internal notes column
    _r.setdefault("Notes / Annotator Comments", "")
FIELDS = list(rows[0].keys())
by_id = {r["Review ID"]: r for r in rows}

# ---------------------------------------------------------------------------
# 1. Unified annotation rule (idempotent re-application)
# ---------------------------------------------------------------------------
RULES = [
    ("HK-C080", "Code-switched", "Intra-sentential",
     "B终核 2026-11-10：Hojicha latte 为通用饮品品类名，非店铺专有全名，"
     "按统一口径由 Chinese 改判 Code-switched (Intra-sentential)。"),
    ("HK-C006", "Code-switched", "Intra-sentential",
     "B终核 2026-11-10：flat white 为国际通用咖啡品类名，不是店铺专有名称；"
     "句末 d 为粤语“啲”的拉丁书写，不计英文。维持 Code-switched (Intra-sentential)。"),
]
for rid, lang, ctype, note in RULES:
    r = by_id[rid]
    r["Language Classification"] = lang
    r["Code-Switching Type"] = ctype
    if note not in r["Notes / Annotator Comments"]:
        r["Notes / Annotator Comments"] = r["Notes / Annotator Comments"].rstrip("；") + "；" + note

# ---------------------------------------------------------------------------
# 2. Verified branch corrections (idempotent)
# ---------------------------------------------------------------------------
LOCATIONS = {
    "HK-C052": "西貢市場街17號地下",
    "HK-C073": "西貢市場街17號地下",
    "HK-C092": "觀塘鴻圖道19號富登中心地下1號舖",
    "HK-C097": "深水埗荔枝角道221號",
    "HK-C107": "新蒲崗爵祿街98號",
}
for rid, branch in LOCATIONS.items():
    by_id[rid]["Branch"] = branch

# ---------------------------------------------------------------------------
# 3. Pre-processing and tokenisation
# ---------------------------------------------------------------------------
converter = opencc.OpenCC("s2t")
EMOJI = re.compile(
    r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    r"\U0001F1E0-\U0001F1FF\U0001F900-\U0001F9FF\U0001FA70-\U0001FAFF"
    r"\u2600-\u26FF\u2700-\u27BF\uFE00-\uFE0F\u200D\U0001F3FB-\U0001F3FF]+"
)


def add_spaces_at_boundaries(text):
    """Insert a space at every Han/Latin transition before segmentation."""
    out, prev = [], None
    for ch in text:
        cp = ord(ch)
        if 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0xF900 <= cp <= 0xFAFF:
            cur = "zh"
        elif ch.isascii() and ch.isalpha():
            cur = "en"
        else:
            cur = "other"
        if prev and cur != "other" and prev != "other" and cur != prev:
            out.append(" ")
        out.append(ch)
        prev = cur
    return "".join(out)


LEXICON = [
    "好飲", "好味", "好食", "好好味", "好好食", "好好飲", "好難飲", "難飲",
    "三文治", "牛角包", "牛油果", "性價比", "份量", "咖啡", "咖啡師", "意粉",
    "沙律", "可麗露", "鮮奶", "焙茶", "質素", "質數", "好煙韌", "口感",
    "忌廉", "酸忌廉", "煙韌", "柚子", "甜度", "薯餅", "蕃薯", "蕃薯條",
    "水準", "豬柳", "帆立貝", "豬柳蛋", "牛柳粒", "蘋果", "豬排", "腐乳",
    "芝士蛋糕", "芝士", "全日早餐", "抵食", "幫襯", "返工", "外賣", "包裝",
    "早餐", "退曬步", "退晒步", "飲品", "食物", "蛋糕", "蛋撻", "卷蛋",
    "牛面頰", "豐富", "美味", "酸種", "酸種麵包", "麵包", "南瓜", "滿足",
    "價錢", "選擇", "驚喜", "配料", "味道", "熱香餅", "煙肉", "冷萃", "拉花",
    "好香", "好正", "好新鮮", "性價比高", "物超所值", "薄脆", "大件夾抵食",
    "冇啦啦", "手多", "太細杯", "淡到水咁", "成杯", "唔識沖", "唔差", "唔錯",
    "唔到", "唔好", "唔會", "唔算", "超級", "勁好", "勁少", "勁多", "勁好食",
    "做gym", "長做長有",
]
for w in LEXICON:
    jieba.add_word(w)

ZH_STOP = set(
    list("的了是在我有和就不人一上也很到說要去對之出會可這而又但同過住個返做得係冇唔嘅咗佢啲喺嚟俾㗎喎啦囉嘛啩咩嘢都太多少大小好來完想比加被從用話先再把畀左下入仲日其番真曬成杯咁幾次過好應即時")
    + ["自己", "真係", "仲要", "冇啦啦", "邊個", "點解", "咁樣", "如果", "或者",
       "可能", "其實", "因為", "所以", "一個", "依然", "雖然"]
)
EN_STOP = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "am", "it", "its",
    "i", "my", "me", "we", "our", "you", "your", "he", "she", "his", "her", "they",
    "them", "their", "this", "that", "these", "those", "and", "or", "but", "not",
    "of", "to", "for", "with", "on", "at", "in", "by", "so", "if", "as", "do",
    "did", "no", "has", "had", "have", "will", "s", "t", "re",
}
BRANDS = {
    "starbucks", "pacific", "mccafe", "mccafé", "foodpanda", "cohee", "fineprint",
    "contrast", "arabica", "%arabica", "miss", "reborn", "alpha", "pause",
    "kinari", "nodi", "fstw", "lungo", "lattehatist", "cupping", "ohms", "panash",
    "yeaffee", "frenchies", "haahim", "idfc", "mcafe", "badgers", "jessy", "cozy",
}


def is_zh(t):
    return any(0x4E00 <= ord(c) <= 0x9FFF or 0x3400 <= ord(c) <= 0x4DBF
               or 0xF900 <= ord(c) <= 0xFAFF for c in t)


def is_en(t):
    return bool(re.match(r"^[a-zA-Z]+$", t))


def prep(text):
    return converter.convert(add_spaces_at_boundaries(EMOJI.sub("", text)))


def tokenize(text):
    out = []
    for w in jieba.cut(prep(text)):
        w = w.strip()
        if not w:
            continue
        lw = w.lower()
        if lw == "d":                       # 啲 written as Latin d
            out.append(("啲", "zh"))
            continue
        if is_en(w):
            if lw not in BRANDS and len(lw) > 1:
                out.append((lw, "en"))
        elif is_zh(w):
            out.append((w, "zh"))
    return out


def split_sentences(text):
    """Split at 。！？!?；;… and ASCII '.' not between digits; commas stay."""
    parts = re.split(r"[。！？!?；;…\n]+|(?<!\d)\.(?!\d)", text)
    return [p for p in parts if p.strip()]


# ---------------------------------------------------------------------------
# 4. Headline statistics
# ---------------------------------------------------------------------------
lang = Counter(r["Language Classification"] for r in rows)
cs = [r for r in rows if r["Language Classification"] == "Code-switched"]
types = Counter(r["Code-Switching Type"] for r in cs)

en_words, zh_words = [], []
for r in cs:
    for token, lg in tokenize(r["Review Text"]):
        if lg == "en":
            if token not in EN_STOP:
                en_words.append(token)
        elif token not in ZH_STOP and len(token) >= 2:
            zh_words.append(token)

en_freq = Counter(en_words)
zh_freq = Counter(zh_words)

# Cross-language bigrams within sentence boundaries only
bigrams = Counter()
bigram_context = {}
for r in cs:
    for sentence in split_sentences(r["Review Text"]):
        toks = tokenize(sentence)
        for i in range(len(toks) - 1):
            (t1, l1), (t2, l2) = toks[i], toks[i + 1]
            if l1 == l2:
                continue
            direction = "ZH→EN" if l1 == "zh" else "EN→ZH"
            key = (t1, t2, direction)
            bigrams[key] += 1
            bigram_context.setdefault(key, (r["Review ID"], sentence.strip()))

# ---------------------------------------------------------------------------
# 5. Semantic domains (no "Other" bucket)
# ---------------------------------------------------------------------------
DOMAINS = {
    "Western Bakery & Food": [
        "bagel", "begal", "muffin", "scone", "pasta", "smoothie", "sourdough",
        "salad", "toast", "pancake", "brunch", "breakfast", "allday", "tiramisu",
        "burger", "cream", "cheese", "caramel", "salted", "french",
    ],
    "Coffee, Tea & Specialty Terms": [
        "cafe", "flat", "white", "creamy", "overextract", "dirty", "shot",
        "extra", "single", "origin", "drip", "bag", "black", "coffee",
        "hojicha", "latte",
    ],
    "Service & Ordering": [
        "keep", "menu", "order", "ordered", "picture", "comment", "bookmarked",
    ],
    "Evaluative & Descriptive": [
        "very", "good", "worth", "price", "must", "try", "tiny", "fresh", "sweet",
    ],
    "Leisure & Activity": ["gym"],
}
word2dom = {w: d for d, words in DOMAINS.items() for w in words}
dom_stats = {d: [0, set()] for d in DOMAINS}
for w, c in en_freq.items():
    d = word2dom.get(w)
    if d is None:
        raise SystemExit(f"Unmapped English word: {w!r} ({c})")
    dom_stats[d][0] += c
    dom_stats[d][1].add(w)

# ---------------------------------------------------------------------------
# 6. Write artefacts
# ---------------------------------------------------------------------------
def write_csv(name, header, data):
    with open(os.path.join(OUT, name), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(data)


write_csv(
    "06_混用评论英文高频词与语义分类表.csv",
    ["English Word", "Frequency", "Semantic Domain"],
    [[w, c, word2dom[w]] for w, c in en_freq.most_common()],
)

ATTRIBUTE = {
    "咖啡": "Target Beverage", "好食": "Taste / Gustatory", "份量": "Portion Size",
    "選擇": "Variety", "意粉": "Food Item", "好味": "Taste / Gustatory",
    "水準": "Consistency", "質素": "Quality", "價錢": "Price / Value",
    "好好食": "Taste (Emphatic)", "煙韌": "Texture (Chewy)",
    "口感": "Mouthfeel / Texture", "好飲": "Taste (Drink)",
    "牛油果": "Ingredient", "麵包": "Food Item",
}
write_csv(
    "07_混用评论中文高频词表.csv",
    ["Chinese Content Word", "Frequency", "Attribute Focus"],
    [[w, c, ATTRIBUTE.get(w, "General Evaluation")] for w, c in zh_freq.most_common()],
)

SYNTAX = {
    ("keep", "住"): "English verb + Cantonese continuous aspect marker (住)",
    ("的", "cafe"): "Chinese genitive particle (的) + English noun",
    ("bagel", "都"): "Topicalised English subject + Cantonese inclusive adverb (都)",
    ("第一", "cafe"): "Ordinal adjective + English loan noun",
    ("muffin", "好好味"): "English subject + Cantonese stative predicate",
    ("menu", "寫"): "English subject + Cantonese verb (寫)",
    ("杯", "creamy"): "Cantonese classifier (杯) + English adjective",
    ("overextract", "曬"): "English technical verb + Cantonese exhaustive particle (曬)",
    ("同", "menu"): "Cantonese relator (同) + English noun",
    ("picture", "嚴重"): "English noun + Chinese predicate adjective",
    ("淡到水咁", "cafe"): "Cantonese simile predicate + English subject",
    ("latte", "呢"): "English beverage noun + Cantonese demonstrative-classifier (呢間)",
}
write_csv(
    "08_跨语言边界Bigram二元语法搭配表.csv",
    ["Token 1", "Token 2", "Transition Direction", "Frequency", "Review ID", "Syntactic Description"],
    [[t1, t2, d, c, bigram_context[(t1, t2, d)][0],
      SYNTAX.get((t1, t2), "Syntactic boundary alternation")]
     for (t1, t2, d), c in bigrams.most_common()],
)

# KWIC: ±35 characters around each keyword occurrence
KEYWORDS = ["bagel", "cafe", "keep", "order", "sourdough", "dirty",
            "flat white", "hojicha latte", "overextract", "extra shot"]
kwic = []
for r in cs:
    text = r["Review Text"]
    low = text.lower()
    for kw in KEYWORDS:
        start = 0
        while True:
            pos = low.find(kw.lower(), start)
            if pos < 0:
                break
            end = pos + len(kw)
            kwic.append([
                r["Review ID"], text[pos:end],
                text[max(0, pos - 35):pos], text[pos:end], text[end:end + 35], text,
            ])
            start = end
write_csv(
    "09_关键词KWIC语境全量数据库.csv",
    ["Review ID", "Keyword", "Left Context", "Center", "Right Context", "Full Text"],
    kwic,
)

def storefront_code(url):
    m = re.search(r"/(?:restaurant|chain)/([a-z0-9]+)/", url)
    return m.group(1) if m else None


stats = {
    "n_total": len(rows),
    "language": {k: [v, round(v / len(rows) * 100, 2)] for k, v in lang.items()},
    "cs_types": {k: [v, round(v / len(cs) * 100, 2)] for k, v in types.items()},
    "en_tokens": len(en_words),
    "en_types": len(en_freq),
    "zh_tokens": len(zh_words),
    "zh_types": len(zh_freq),
    "bigram_tokens": sum(bigrams.values()),
    "bigram_types": len(bigrams),
    "domains": {d: [n, len(s)] for d, (n, s) in dom_stats.items()},
    "unique_url_strings": len({r["Source URL"] for r in rows}),
    "unique_storefront_codes": len({c for r in rows if (c := storefront_code(r["Source URL"]))}),
    "unique_brands": len({r["Brand"] for r in rows}),
    "sample_audited": 26,
    "sample_pct": round(26 / len(rows) * 100, 2),
}
with open(os.path.join(OUT, "nlp_analysis_results_perfect.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------------------
# 7. Console summary
# ---------------------------------------------------------------------------
print(f"N = {len(rows)}")
print("Language:", dict(lang))
print("CS types:", dict(types))
print(f"EN tokens/types = {len(en_words)}/{len(en_freq)}")
print(f"ZH tokens/types = {len(zh_words)}/{len(zh_freq)}")
print(f"Bigrams tokens/types = {sum(bigrams.values())}/{len(bigrams)}")
for d, (n, s) in dom_stats.items():
    print(f"  {d}: {n} tokens / {len(s)} types")
print("Top bigrams:")
for k, v in bigrams.most_common(10):
    print("  ", k, v, bigram_context[k][0])
print("Wrote:", OUT)
