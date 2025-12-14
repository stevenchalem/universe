# KG Population Pipeline

**Goal:** Build a generalizable pipeline that can discover domain concepts, attach them to GIST, and extract instances/relationships from any corpus.

**Test corpus:** ~30K Universe Today articles (astronomy/space news)

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Input: Article Corpus                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 1: Topic Classification                                      │
│  • Input: Raw article text/HTML                                    │
│  • Output: Relevant gist topics (e.g., ["events", "geo", "time"])  │
│  • Method: Keyword matching or LLM                                 │
│  • File: topic_classifier.py                                       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 2: Schema Subsetting                                         │
│  • Input: Topic list from Step 1                                   │
│  • Output: Relevant gist classes & properties                      │
│  • Method: Graph traversal from topic seeds                        │
│  • File: gist_schema.py                                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 3: Entity Extraction [TODO]                                  │
│  • Input: Article + Schema subset                                  │
│  • Output: Entity candidates with types & confidence               │
│  • Method: LLM with schema-grounded prompt                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 4: Schema Bootstrapping [TODO]                               │
│  • Input: Entity candidates, gist schema                           │
│  • Output: Proposed domain subclasses (e.g., "Exoplanet")          │
│  • Method: LLM proposes, human reviews via Schema Workbench        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 5: Relationship Extraction [TODO]                            │
│  • Input: Article + Resolved entities + Schema subset              │
│  • Output: Triple candidates (subject, predicate, object)          │
│  • Method: LLM with entity context                                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 6: Entity Resolution [TODO]                                  │
│  • Input: Entity mentions across articles                          │
│  • Output: Merged entity URIs                                      │
│  • Method: Similarity + LLM disambiguation                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STEP 7: Review Interface [TODO]                                   │
│  • Input: Candidate triples with confidence scores                 │
│  • Output: Approved triples for graph store                        │
│  • Method: Human review queue (high confidence → auto-approve)     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Output: Knowledge Graph                         │
│                  (RDF triples in graph store)                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Current Status

### ✅ Completed

1. **gist Schema Loader** ([gist_schema.py](gist_schema.py))
   - Loads gistCore ontology
   - Subsetting by topics or specific classes
   - Generates LLM-ready schema text

2. **Topic Classifier** ([topic_classifier.py](topic_classifier.py))
   - Keyword-based classifier (fast, no API needed)
   - LLM-based classifier (more accurate, requires Anthropic API)
   - Hybrid mode (keyword filter → LLM refinement)

3. **Topic Seeds** ([gist_schema.py](gist_schema.py):16-65)
   - Defined for 11 topics: organizations, events, time, geo, agreements, quantities, content, collections, categories, artifacts, intentions

### 🚧 Next Steps

4. **Entity Extraction Engine**
   - Use schema subset + article → extract typed entities
   - Confidence scoring
   - Batch processing with progress tracking

5. **Schema Bootstrapping**
   - Analyze entity candidates across corpus
   - Propose domain-specific subclasses (e.g., `ut:Exoplanet rdfs:subClassOf gist:Category`)
   - Human approval workflow

6. **Relationship Extraction**
   - Two-stage: entities first, then relationships
   - Context window: resolved entities + article excerpt
   - Schema-guided relation prediction

7. **Entity Resolution**
   - String similarity + embedding similarity
   - LLM-based disambiguation for close matches
   - Merge entity mentions → canonical URIs

## Design Principles

### GIST-First Modeling

- **Use gist classes wherever possible** - Don't create `ut:Mission` when `gist:Event` or `gist:Project` fits
- **Create domain subclasses only when needed** - E.g., `ut:Exoplanet rdfs:subClassOf gist:Category`
- **Attach at the right level** - Subclass the most specific applicable gist class

### Human-in-the-Loop

- **Schema decisions require approval** - Proposed subclasses go to Schema Workbench
- **High-confidence extractions auto-approve** - Saves review time
- **Corrections improve extraction** - Active learning from human feedback

### Confidence-Driven Workflow

- **High confidence (>0.9)** → Graph store
- **Medium confidence (0.5-0.9)** → Review queue
- **Low confidence (<0.5)** → Discard or flag for future improvement

## Usage

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download gist ontology (if not present)
# Visit https://www.semanticarts.com/gist/

# Classify sample articles
python topic_classifier.py

# Run full pipeline demo
python pipeline_demo.py
```

### API Examples

#### Topic Classification

```python
from topic_classifier import KeywordTopicClassifier
from pathlib import Path

# Create classifier
classifier = KeywordTopicClassifier(min_confidence=0.1)

# Classify an article
article_path = Path("articles/articles_some-article.html")
result = classifier.classify(article_path.read_text())

print(f"Topics: {result.topics}")
print(f"Confidence: {result.confidence}")
```

#### Schema Subsetting

```python
from gist_schema import GistSchema

# Load gist
schema = GistSchema("gistCore14_0_0.ttl")

# Get subset for specific topics
subset = schema.subset_by_topics(["events", "time", "geo"])

# Generate LLM prompt
schema_text = subset.to_prompt_text()
print(schema_text)

# Or subset by specific classes
subset = schema.subset_by_classes(["Event", "Person", "Organization"])
```

#### Full Pipeline

```python
from pipeline_demo import demo_pipeline
from pathlib import Path

article = Path("articles/articles_some-article.html")
classification, subset, schema_text = demo_pipeline(
    article,
    "gistCore14_0_0.ttl"
)

# Use schema_text in extraction prompt
extraction_prompt = f"""
{schema_text}

Extract entities and relationships from this article:
{article.read_text()}
"""
```

## File Structure

```
c:\repos\universe\
├── gist_schema.py           # Schema loader & subsetter
├── topic_classifier.py      # Topic classification
├── pipeline_demo.py         # End-to-end demo
├── download_articles.py     # Article scraper
├── requirements.txt         # Python dependencies
├── PIPELINE.md             # This file
├── gistCore_llm_reference.md  # Human-readable gist reference
├── gistCore14_0_0.ttl      # gist ontology (download separately)
└── articles/               # Downloaded articles
    ├── articles_*.html
    └── articles_*.html.json
```

## Topic Definitions

Each topic maps to seed classes in gist. The subsetter automatically includes:
- Seed classes
- All superclasses (for hierarchy context)
- Subclasses (up to 2 levels deep)
- Relevant properties (domain/range matching)

| Topic | Seed Classes | Use Cases |
|-------|-------------|-----------|
| **organizations** | Organization, GovernmentOrganization, Person | NASA, ESA, research teams |
| **events** | Event, HistoricalEvent, PhysicalEvent, Task | Launches, discoveries, missions |
| **time** | TimeInterval, TemporalRelation | Dates, durations, timelines |
| **geo** | GeoLocation, GeoRegion, GeoPoint | Planets, landing sites, regions |
| **agreements** | Agreement, Contract, Commitment | Partnerships, MOUs |
| **quantities** | Magnitude, UnitOfMeasure, Aspect | Distances, masses, velocities |
| **content** | Content, ContentExpression, Message | Images, papers, signals |
| **collections** | Collection, Network | Catalogs, constellations |
| **categories** | Category, Tag | Object types, classifications |
| **artifacts** | Equipment, PhysicalIdentifiableItem | Spacecraft, instruments |
| **intentions** | Intention, Requirement, Specification | Mission goals, requirements |

## Configuration

### Topic Classifier

Adjust classification behavior:

```python
# Stricter keyword matching
classifier = KeywordTopicClassifier(min_confidence=0.2)

# More lenient
classifier = KeywordTopicClassifier(min_confidence=0.05)

# Use LLM (requires Anthropic API key)
from topic_classifier import LLMTopicClassifier
classifier = LLMTopicClassifier(
    model="claude-3-haiku-20240307",
    min_confidence=0.6
)

# Hybrid (fast keyword filter, then LLM refinement)
from topic_classifier import HybridTopicClassifier
classifier = HybridTopicClassifier(
    keyword_threshold=0.05,
    llm_threshold=0.6
)
```

### Schema Subsetter

```python
# Include or exclude descendants
subset = schema.subset_by_topics(
    ["events", "organizations"],
    include_descendants=True  # default: True
)

# Control prompt verbosity
schema_text = subset.to_prompt_text(
    max_definition_len=120  # truncate long definitions
)
```

## Testing

```bash
# Test topic classifier on sample articles
python topic_classifier.py

# Test full pipeline (requires gist ontology)
python pipeline_demo.py

# Batch classify articles
python -c "
from pipeline_demo import batch_classify_articles
from pathlib import Path
batch_classify_articles(
    Path('articles'),
    Path('classifications.json'),
    limit=1000
)
"
```

## Next Implementation: Entity Extraction

The entity extraction engine will:

1. Take article text + schema subset
2. Use LLM to identify entities with types
3. Output structured JSON with confidence scores

**Example output:**

```json
{
  "entities": [
    {
      "text": "James Webb Space Telescope",
      "type": "gist:Equipment",
      "confidence": 0.95,
      "mentions": ["offset:123", "offset:456"]
    },
    {
      "text": "NASA",
      "type": "gist:GovernmentOrganization",
      "confidence": 0.98,
      "mentions": ["offset:234"]
    }
  ]
}
```

See architecture diagram for full extraction → resolution → graph flow.

## References

- gist ontology: https://www.semanticarts.com/gist/
- Semantic Arts gist documentation: https://w3id.org/semanticarts/gist
- Universe Today (corpus source): https://www.universetoday.com/
- Creative Commons BY 4.0: https://creativecommons.org/licenses/by/4.0/
