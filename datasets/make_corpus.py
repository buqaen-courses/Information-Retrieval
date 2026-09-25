"""Deterministic (seeded) generator for the shared course datasets.

Generates, with fixed seeds:
- ``corpus/``: ~200 short .txt docs across 6 topics (doc-001.txt …)
- ``qrels.json``: relevance judgments for ~10 queries (graded 1-2)
- ``fallback_products.json``: 120 products (4 categories x 30) with
  ~8 deliberate near-duplicate descriptions (used S18-S23 if a crawl fails).

Usage:
    python datasets/make_corpus.py

Every session reads this same data. Re-running produces identical output.
"""
from __future__ import annotations

import json
import random
from pathlib import Path

SEED = 42
DOCS_PER_TOPIC = 34  # 6 topics x 34 = 204 docs
OUT_DIR = Path(__file__).resolve().parent

TOPICS: dict[str, list[str]] = {
    "python": [
        "Python functions accept arguments and return values.",
        "A virtual environment isolates project dependencies cleanly.",
        "Lists and dictionaries store collections of objects.",
        "The requests library downloads web pages with one call.",
        "Debugging with print statements reveals program state.",
        "Classes bundle data and methods into reusable objects.",
    ],
    "football": [
        "The striker scored twice in the second half.",
        "A corner kick created chaos inside the penalty box.",
        "The goalkeeper saved a powerful long range shot.",
        "Midfield pressing forced several costly turnovers.",
        "The referee showed a yellow card for the late tackle.",
        "Extra time decided a tense cup final again.",
    ],
    "cooking": [
        "Simmer the tomato sauce for twenty minutes.",
        "Season the chicken generously with salt and pepper.",
        "Bake the bread until the crust turns golden.",
        "Chop fresh basil and stir it into the pasta.",
        "Caramelized onions add sweetness to any stew.",
        "Let the dough rest before rolling it thin.",
    ],
    "space": [
        "Mars rovers analyze rocks for signs of water.",
        "Jupiter storms have raged for hundreds of years.",
        "Telescopes collect light from distant galaxies.",
        "Astronauts train for months before every mission.",
        "Saturn rings consist of ice and rock particles.",
        "Exoplanet surveys reveal thousands of new worlds.",
    ],
    "movies": [
        "The director framed every shot with unusual symmetry.",
        "A plot twist in act three surprised the audience.",
        "The soundtrack swelled during the final chase scene.",
        "Critics praised the lead actor restrained performance.",
        "Animated films blend humor with emotional depth.",
        "The sequel expanded the original story world.",
    ],
    "travel": [
        "Night trains cross the mountains before dawn.",
        "Street markets sell spices, textiles, and souvenirs.",
        "A harbor ferry connects the islands every hour.",
        "Backpackers trade route tips in busy hostels.",
        "Desert sunsets paint the dunes in deep orange.",
        "Budget airlines opened new weekend destinations.",
    ],
}

QUERIES: list[tuple[str, str]] = [
    ("q01", "python virtual environment dependencies"),
    ("q02", "requests library download web pages"),
    ("q03", "striker scored second half"),
    ("q04", "goalkeeper saved shot"),
    ("q05", "tomato sauce simmer"),
    ("q06", "bake bread golden crust"),
    ("q07", "Mars rover water rocks"),
    ("q08", "telescopes distant galaxies"),
    ("q09", "plot twist film audience"),
    ("q10", "night trains mountains"),
]

QUERY_TOPICS = ["python", "python", "football", "football", "cooking",
                "cooking", "space", "space", "movies", "travel"]

PRODUCT_CATEGORIES = ["electronics", "books", "kitchen", "sports"]
PRODUCT_ADJ = ["compact", "durable", "lightweight", "premium", "classic",
               "wireless", "ergonomic", "stainless", "portable", "quiet"]
PRODUCT_NOUNS = ["headphones", "kettle", "backpack", "lamp", "speaker",
                 "notebook", "bottle", "tent", "keyboard", "mug"]


def make_documents(rng: random.Random) -> list[tuple[str, str, str]]:
    """Return (doc_id, topic, text) triples, deterministically shuffled."""
    docs: list[tuple[str, str, str]] = []
    n = 0
    for topic, sentences in TOPICS.items():
        for _ in range(DOCS_PER_TOPIC):
            n += 1
            k = rng.randint(3, 5)
            picked = [rng.choice(sentences) for _ in range(k)]
            title = picked[0]
            text = title + "\n" + " ".join(picked)
            docs.append((f"doc-{n:03d}", topic, text))
    rng.shuffle(docs)
    # Re-number after shuffle so ids are stable AND shuffled across topics.
    renumbered = [(f"doc-{i + 1:03d}", t, x) for i, (_, t, x) in enumerate(docs)]
    return renumbered


def make_qrels(docs: list[tuple[str, str, str]]) -> dict:
    """Grade docs per query: 2 if doc contains >=2 query terms, else 1 (same topic)."""
    by_topic: dict[str, list[str]] = {}
    for doc_id, topic, _ in docs:
        by_topic.setdefault(topic, []).append(doc_id)
    texts = {d: t.lower() for d, _, t in docs}
    qrels: dict = {}
    for (qid, qtext), topic in zip(QUERIES, QUERY_TOPICS):
        terms = qtext.lower().split()
        judged: dict[str, int] = {}
        for doc_id in by_topic[topic]:
            hits = sum(1 for w in terms if w in texts[doc_id])
            judged[doc_id] = 2 if hits >= 2 else 1
        qrels[qid] = {"query": qtext, "topic": topic, "relevant": judged}
    return qrels


def make_products(rng: random.Random) -> list[dict]:
    """Build 120 products; last 8 of sports are near-duplicates of earlier ones."""
    products: list[dict] = []
    pid = 0
    for cat in PRODUCT_CATEGORIES:
        for i in range(30):
            pid += 1
            adj = PRODUCT_ADJ[(pid + i) % len(PRODUCT_ADJ)]
            noun = PRODUCT_NOUNS[(pid * 3 + i) % len(PRODUCT_NOUNS)]
            price = round(rng.uniform(5, 500), 2)
            desc = (
                f"A {adj} {noun} for {cat} lovers. "
                f"Highly rated {noun} with reliable everyday performance."
            )
            products.append(
                {"id": f"p-{pid:03d}", "name": f"{adj.title()} {noun} {i + 1}",
                 "price": price, "description": desc, "category": cat}
            )
    # 8 deliberate near-duplicates: copy description, tweak one word.
    for j in range(8):
        src = products[j * 7]
        dup = dict(src)
        dup["id"] = f"p-{121 + j:03d}"
        dup["name"] = src["name"] + " Plus"
        dup["description"] = src["description"].replace("Highly rated", "Top rated")
        dup["price"] = round(src["price"] + 1.0, 2)
        products.append(dup)
    return products


def main() -> None:
    rng = random.Random(SEED)
    docs = make_documents(rng)

    corpus_dir = OUT_DIR / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    for old in corpus_dir.glob("*.txt"):
        old.unlink()
    for doc_id, topic, text in docs:
        (corpus_dir / f"{doc_id}.txt").write_text(
            f"topic: {topic}\n{text}\n", encoding="utf-8")

    qrels = make_qrels(docs)
    (OUT_DIR / "qrels.json").write_text(json.dumps(qrels, indent=2), encoding="utf-8")

    products = make_products(rng)
    (OUT_DIR / "fallback_products.json").write_text(
        json.dumps(products, indent=2), encoding="utf-8")

    print(f"docs: {len(docs)}")
    print(f"queries: {len(qrels)}")
    print(f"products: {len(products)}")


if __name__ == "__main__":
    main()
