# Handoff: KG Population Pipeline with GIST

## Context

Building a generalizable knowledge graph population system that extracts structured data from unstructured text using GIST upper ontology as the foundation. Test corpus is 30K Universe Today articles (astronomy/space), but the method should work for any domain.

**Approach:** GIST-first modeling. Use gist classes directly where they fit, create domain subclasses of gist classes when needed. Human-in-the-loop for schema decisions, automated extraction with confidence scoring.

---

## Completed Components

### 1. `gist_schema.py` — Schema loading and subsetting

Loads gistCore TTL via rdflib, provides topic-based subsetting for prompt construction.

```python
from gist_schema import GistSchema, available_topics

schema = GistSchema("gistCore14_0_0.ttl")
subset = schema.subset_by_topics(["organizations", "events", "time"])
prompt_text = subset.to_prompt_text()
```

**Key methods:**
- `GistSchema(path)` — load ontology
- `schema.subset_by_topics(["events", "organizations"])` — get relevant subset
- `schema.subset_by_classes(["Agreement", "Person"])` — subset by specific classes
- `subset.to_prompt_text()` — generate LLM-friendly schema fragment
- `subset.stats()` — get counts of classes/properties

**Available topics:** agreements, artifacts, categories, collections, content, events, geo, intentions, organizations, quantities, time

---

### 2. `topic_classifier.py` — Keyword-based topic detection

Fast first-pass classifier using keyword matching and regex patterns.

```python
from topic_classifier import TopicClassifier, classify_text

# Quick usage
topics = classify_text(article_text)  # Returns list like ["events", "organizations", "geo"]

# Detailed usage
classifier = TopicClassifier()
result = classifier.classify(article_text)
print(result.topics)           # Topics that passed threshold
print(result.scores)           # Raw scores per topic
print(result.matched_keywords) # Which keywords matched
```

**Corpus testing:**
```bash
python topic_classifier.py /path/to/html/corpus 500
```

Shows coverage stats and identifies articles with zero topic matches (candidates for LLM fallback or keyword expansion).

---

### 3. `gistCore_llm_reference.md` — Full schema reference

Complete LLM-friendly summary of gistCore 14.0.0 with:
- Modeling pattern guidance (Magnitudes, Temporal, Agreements, etc.)
- Class hierarchy with definitions
- Property hierarchy with domains/ranges
- Statistics

---

## Pipeline Architecture

```
                    ┌─────────────────┐
                    │  Topic          │
Article ──────────► │  Classifier     │ ──► ["events", "organizations", "geo"]
                    │  (keywords)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Schema         │
                    │  Subsetter      │ ──► Relevant classes + properties
                    │                 │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Extraction     │
                    │  Engine         │ ──► Candidate triples + confidence
                    │  (LLM)          │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Entity         │
                    │  Resolver       │ ──► Deduplicated entities
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Review         │
                    │  Interface      │ ◄──► Human approval
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Graph          │
                    │  Store          │
                    └─────────────────┘
```

### Component Status

| Component | Status | File |
|-----------|--------|------|
| Schema subsetter | ✅ Done | `gist_schema.py` |
| Topic classifier (keywords) | ✅ Done | `topic_classifier.py` |
| Topic classifier (LLM fallback) | ⬜ Todo | — |
| Entity extractor | ⬜ Todo | — |
| Relationship extractor | ⬜ Todo | — |
| Entity resolver | ⬜ Todo | — |
| Validation | ⬜ Todo | — |
| Review interface | ⬜ Todo | — |

---

## Next Steps

### Immediate: Test topic classifier on real corpus

```bash
python topic_classifier.py /path/to/universetoday 500
```

This will reveal:
- Which topics are most common
- Which articles get zero matches (need keyword expansion or LLM fallback)
- Whether thresholds need tuning

### Then: Build extraction engine

Two-pass approach:
1. **Entity extraction** — text + schema → candidate entities with types
2. **Relationship extraction** — text + entities + schema → candidate triples

**Output format per triple:**
```json
{
  "subject": {
    "mention": "Perseverance",
    "proposed_type": "astro:Rover",
    "identifiers": ["NASA Perseverance", "Mars 2020 rover"]
  },
  "predicate": "gist:isParticipantIn",
  "object": {
    "mention": "the Mars 2020 mission",
    "proposed_type": "astro:Mission",
    "identifiers": ["Mars 2020"]
  },
  "confidence": 0.9,
  "source_span": "Perseverance, the rover at the heart of NASA's Mars 2020 mission...",
  "source_sentence_index": 3
}
```

---

## Files

| File | Description |
|------|-------------|
| `gist_schema.py` | Schema loading and subsetting |
| `topic_classifier.py` | Keyword-based topic detection |
| `gistCore14_0_0.ttl` | GIST 14.0.0 ontology (Turtle) |
| `gistCore_llm_reference.md` | Full LLM-friendly schema reference |
| `HANDOFF.md` | This file |

## Dependencies

```bash
pip install rdflib
```

---

## Usage Example: Full Flow

```python
from gist_schema import GistSchema
from topic_classifier import TopicClassifier

# Load once at startup
schema = GistSchema("gistCore14_0_0.ttl")
classifier = TopicClassifier()

# Per article
article_text = "NASA's Perseverance rover discovered..."

# 1. Classify topics
result = classifier.classify(article_text)
topics = result.topics  # ["organizations", "events", "artifacts", "geo"]

# 2. Get relevant schema subset
subset = schema.subset_by_topics(topics)
schema_text = subset.to_prompt_text()

# 3. Build extraction prompt (TODO)
prompt = f"""
Given this schema:
{schema_text}

Extract entities and relationships from:
{article_text}
"""

# 4. Call LLM, parse response, validate, store...
```

---

## Domain Extension Pattern

For Universe Today (astronomy), anticipated domain classes:

```
gist:PhysicalSubstance
  └─ astro:CelestialBody
       ├─ astro:Star
       ├─ astro:Planet
       ├─ astro:Moon
       └─ astro:Galaxy

gist:PhysicalIdentifiableItem
  └─ astro:Spacecraft
       ├─ astro:Orbiter
       ├─ astro:Lander
       └─ astro:Rover

gist:Event
  └─ astro:Mission
  └─ astro:AstronomicalEvent
```

Schema bootstrapping workflow:
1. LLM proposes domain classes from corpus samples
2. Human reviews, positions in hierarchy, approves/rejects
3. Approved classes added to domain ontology
4. Domain ontology imports gistCore
