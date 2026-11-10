# Annotation rules

Unit of analysis: the complete review (language category, switching type); word tokens (frequency); adjacent token pairs across a language boundary (bigrams).

## Language category (one per review)
- **Chinese**: Chinese only, including written Cantonese (e.g. 佢, 唔, 嘅) and Cantonese particles (啦, 喎, 㗎).
- **English**: English only.
- **Code-switched**: contains ordinary English words in Latin letters together with Chinese.
- **Other/uncertain**: other languages dominate, or the language cannot be judged.

## Boundary rules
1. Brand names, shop names and merchant-specific (proprietary) product names do not by themselves make a review code-switched. Generic English category words (flat white, bagel, hojicha latte) count as English even when they appear on a menu.
2. Loanwords written in Chinese characters (拿鐵, 芝士) are Chinese; the same word written in English (latte, cheese) is English.
3. Pinyin and pinyin abbreviations (yyds) are Chinese; English abbreviations (OMG, lol) are English.
4. If the only English item in a Chinese review is a very common word (OK, App, WiFi), the review is Chinese.
5. Emoji, numbers and prices (HK$15) are ignored.
6. The Cantonese written form "d" (啲) is not English.

## Switching type (Code-switched reviews; a review may have several)
- **Intra-sentential**: English inside a Chinese sentence or clause.
- **Inter-sentential**: one sentence in Chinese, another in English.
- **Tag**: an isolated English exclamation or tag at the start or end of a sentence (e.g. "bookmarked!").

## Recorded boundary decisions
- HK-C006 "flat white", HK-C080 "Hojicha latte", HK-C085 "dirty" and HK-C113 "allday breakfast": generic drink or food categories, so Code-switched (HK-C080 was relabeled from Chinese in the final check).
- HK-C038 "CP值": conventionalised Chinese abbreviation (value for money), so Chinese.
- HK-C119: "酸種麵包" and "bagel" refer to two different items (a wrong order), not equivalent forms.
