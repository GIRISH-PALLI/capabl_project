from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
import yfinance as yf


@dataclass
class NewsItem:
    title: str
    summary: str
    publisher: str
    link: str


@dataclass
class SentimentReport:
    label: str
    score: float
    source: str
    sample_size: int


def _lexicon_score(text: str) -> float:
    positive = {
        "gain",
        "beats",
        "surge",
        "growth",
        "upgrade",
        "strong",
        "record",
        "bullish",
        "profit",
        "outperform",
    }
    negative = {
        "drop",
        "miss",
        "fall",
        "downgrade",
        "weak",
        "loss",
        "bearish",
        "risk",
        "investigation",
        "lawsuit",
    }

    words = [token.strip(".,!?;:\"'()[]{}").lower() for token in text.split()]
    words = [word for word in words if word]
    if not words:
        return 0.0

    pos_count = sum(1 for word in words if word in positive)
    neg_count = sum(1 for word in words if word in negative)
    return (pos_count - neg_count) / max(1, len(words))


def _simple_label(score: float) -> str:
    if score > 0.05:
        return "positive"
    if score < -0.05:
        return "negative"
    return "neutral"


def _score_with_vader(text: str) -> float | None:
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except Exception:
        return None

    analyzer = SentimentIntensityAnalyzer()
    return float(analyzer.polarity_scores(text).get("compound", 0.0))


def _score_with_textblob(text: str) -> float | None:
    try:
        from textblob import TextBlob
    except Exception:
        return None

    return float(TextBlob(text).sentiment.polarity)


def _score_with_transformer(text: str) -> float | None:
    try:
        from transformers import pipeline
    except Exception:
        return None

    classifier = pipeline("sentiment-analysis")
    output = classifier(text[:512])[0]
    label = str(output.get("label", "")).upper()
    confidence = float(output.get("score", 0.0))
    signed_score = confidence if "POS" in label else -confidence
    return signed_score


def fetch_news_items(ticker: str, max_items: int = 10) -> list[NewsItem]:
    clean_ticker = (ticker or "").strip().upper()
    if not clean_ticker:
        return []

    try:
        raw_news: list[dict[str, Any]] = yf.Ticker(clean_ticker).news or []
    except Exception:
        return []

    items: list[NewsItem] = []
    for payload in raw_news[:max_items]:
        title = str(payload.get("title") or "")
        summary = str(payload.get("summary") or payload.get("type") or "")
        publisher = str(payload.get("publisher") or "Unknown")
        link = str(payload.get("link") or "")
        if title:
            items.append(NewsItem(title=title, summary=summary, publisher=publisher, link=link))

    return items


def _aggregate_scores(scores: list[float]) -> float:
    if not scores:
        return 0.0
    return float(pd.Series(scores).mean())


def analyze_sentiment_simple(news_items: list[NewsItem]) -> SentimentReport:
    if not news_items:
        return SentimentReport(label="neutral", score=0.0, source="none", sample_size=0)

    scores: list[float] = []
    source = "lexicon"

    for item in news_items:
        text = f"{item.title}. {item.summary}".strip()

        score = _score_with_vader(text)
        if score is not None:
            source = "vader"
        else:
            score = _score_with_textblob(text)
            if score is not None:
                source = "textblob"
            else:
                score = _lexicon_score(text)
                source = "lexicon"

        scores.append(float(score))

    aggregate = _aggregate_scores(scores)
    return SentimentReport(
        label=_simple_label(aggregate),
        score=aggregate,
        source=source,
        sample_size=len(scores),
    )


def analyze_sentiment_transformer(news_items: list[NewsItem]) -> SentimentReport:
    if not news_items:
        return SentimentReport(label="neutral", score=0.0, source="none", sample_size=0)

    scores: list[float] = []
    for item in news_items:
        text = f"{item.title}. {item.summary}".strip()
        score = _score_with_transformer(text)
        if score is None:
            return analyze_sentiment_simple(news_items)
        scores.append(score)

    aggregate = _aggregate_scores(scores)
    return SentimentReport(
        label=_simple_label(aggregate),
        score=aggregate,
        source="transformer",
        sample_size=len(scores),
    )
