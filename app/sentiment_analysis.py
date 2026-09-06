"""
CineVerse Sentiment Analyzer
-----------------------------
Review text లో positive/negative keywords ఎన్ని ఉన్నాయో లెక్కపెట్టి,
"Positive" / "Negative" / "Neutral" అని classify చేస్తుంది.
(తేలికైన, explainable, rule-based NLP approach — external API అవసరం లేదు.)
"""

import re

POSITIVE_WORDS = {
    "good", "great", "excellent", "amazing", "awesome", "fantastic", "love", "loved",
    "best", "brilliant", "wonderful", "superb", "outstanding", "perfect", "enjoyed",
    "enjoyable", "masterpiece", "beautiful", "impressive", "entertaining", "fun",
    "engaging", "gripping", "solid", "recommend", "recommended", "top", "nice",
    "incredible", "stunning", "satisfying", "delightful", "captivating",
}

NEGATIVE_WORDS = {
    "bad", "worst", "terrible", "awful", "boring", "waste", "poor", "disappointing",
    "disappointed", "hate", "hated", "horrible", "weak", "dull", "flop", "mediocre",
    "predictable", "annoying", "slow", "confusing", "bland", "cliche", "cliché",
    "overrated", "forgettable", "underwhelming", "messy", "flat",
}

NEGATION_WORDS = {"not", "never", "no", "n't", "hardly", "barely"}


def analyze_sentiment(text: str) -> str:
    """
    Review text తీసుకుని "Positive", "Negative", లేదా "Neutral" తిరిగి ఇస్తుంది.
    Simple negation handling: "not good" లాంటి phrases ని flip చేస్తుంది.
    """
    if not text:
        return "Neutral"

    words = re.findall(r"[a-zA-Z']+", text.lower())

    score = 0
    for i, word in enumerate(words):
        negated = i > 0 and words[i - 1] in NEGATION_WORDS

        if word in POSITIVE_WORDS:
            score += -1 if negated else 1
        elif word in NEGATIVE_WORDS:
            score += 1 if negated else -1

    if score > 0:
        return "Positive"
    elif score < 0:
        return "Negative"
    else:
        return "Neutral"