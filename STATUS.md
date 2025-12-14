# Project Status: Generalizable KG Population Pipeline

**Last Updated:** 2025-12-14

## What's Built

### 1. Topic Classifier ✅

**File:** [topic_classifier.py](topic_classifier.py)

Three classifier modes:
- **KeywordTopicClassifier** - Fast regex-based matching, no API needed
- **LLMTopicClassifier** - Accurate Claude-based classification, requires API
- **HybridTopicClassifier** - Best of both (keyword filter → LLM refinement)

**Input:** Article HTML or text
**Output:** List of relevant gist topics with confidence scores

**Topics supported:** organizations, events, time, geo, agreements, quantities, content, collections, categories, artifacts, intentions

**Example:**
```python
classifier = KeywordTopicClassifier(min_confidence=0.1)
result = classifier.classify(article_text)
# result.topics = ["events", "geo", "time", "organizations"]
# result.confidence = {"events": 0.85, "geo": 0.92, ...}
```

### 2. Schema Subsetter ✅

**File:** [gist_schema.py](gist_schema.py)

Loads gistCore ontology and extracts topic-relevant subsets.

**Features:**
- Load from gistCore TTL file
- Subset by topics (uses topic seeds)
- Subset by specific classes
- Auto-includes ancestors, descendants, relevant properties
- Generates LLM-ready schema text

**Example:**
```python
schema = GistSchema("gistCore14_0_0.ttl")
subset = schema.subset_by_topics(["events", "time", "geo"])
prompt_text = subset.to_prompt_text()  # Ready for LLM
```

### 3. Topic Seeds ✅

**File:** [gist_schema.py](gist_schema.py) lines 17-113

Defined mappings from topics to gist classes and properties.

**Coverage:**
- 11 topics
- 100+ seed classes
- 60+ explicitly associated properties

### 4. Integration Demo ✅

**File:** [pipeline_demo.py](pipeline_demo.py)

End-to-end demonstration:
1. Classify article topics
2. Generate schema subset
3. Show extraction prompt preview
4. Batch processing capabilities

**Usage:**
```bash
python pipeline_demo.py
```

### 5. Documentation ✅

- **[PIPELINE.md](PIPELINE.md)** - Full pipeline architecture and usage
- **[gistCore_llm_reference.md](gistCore_llm_reference.md)** - Human-readable gist reference
- **[download_articles.md](download_articles.md)** - Article scraper docs

## Testing Results

Tested on Universe Today articles:

```
Article: "1.2 Billion Years Ago, a 1-km Asteroid Smashed into Scotland"
Topics: events, time, geo, content, organizations, quantities, categories
Confidence:
  events         1.00 (100%)
  time           1.00 (100%)
  geo            1.00 (100%)
  content        0.72 (72%)
  organizations  0.54 (54%)
```

Schema subset for these topics:
- 50+ classes (Event, Organization, GeoLocation, etc.)
- 40+ object properties
- 30+ datatype properties

## What's Next

### Immediate Next Step: Entity Extraction Engine

**Goal:** Extract typed entities from articles using schema subset.

**Input:**
- Article text
- Schema subset (from topic classification)

**Output:**
```json
{
  "entities": [
    {
      "text": "James Webb Space Telescope",
      "type": "gist:Equipment",
      "confidence": 0.95,
      "offsets": [[123, 151]]
    }
  ]
}
```

**Approach:**
1. Build extraction prompt: schema subset + article + instructions
2. LLM extracts entities with types
3. Parse structured JSON output
4. Confidence scoring
5. Batch processing with caching

### Subsequent Steps

1. **Schema Bootstrapping** - Propose domain subclasses (e.g., `ut:Exoplanet rdfs:subClassOf gist:Category`)
2. **Relationship Extraction** - Extract triples using resolved entities
3. **Entity Resolution** - Merge duplicate entities across articles
4. **Review Interface** - Human-in-the-loop for uncertain extractions
5. **Graph Store Integration** - Load approved triples into triplestore

## Key Design Decisions

### ✅ Confirmed

1. **GIST-first modeling** - Use gist classes wherever possible, only create subclasses when needed
2. **Two-stage extraction** - Entities first, then relationships (with resolved entity context)
3. **Topic-based subsetting** - Reduces schema size for extraction prompts
4. **Confidence-driven workflow** - High confidence auto-approved, uncertain → review queue
5. **Human-in-the-loop for schema** - New domain classes require approval

### 🤔 Open Questions

1. **Graph store choice** - RDFLib in-memory? GraphDB? Jena Fuseki? Neptune?
2. **Entity resolution strategy** - When to merge entities? Threshold for "same entity"?
3. **Active learning feedback** - How to improve extraction from corrections?
4. **Batch size** - Process articles in batches of 10? 100? Stream?

## Files

```
c:\repos\universe\
├── gist_schema.py              # Schema loader (454 lines)
├── topic_classifier.py         # Topic classification (334 lines)  ← NEW
├── pipeline_demo.py            # Integration demo (170 lines)     ← NEW
├── PIPELINE.md                 # Architecture docs                ← NEW
├── STATUS.md                   # This file                        ← NEW
├── gistCore_llm_reference.md   # gist reference
├── download_articles.py        # Article scraper
├── requirements.txt            # Dependencies (updated)
└── articles/                   # ~30K articles
```

## Dependencies

```
requests>=2.31.0           # Article downloading
beautifulsoup4>=4.12.0     # HTML parsing          ← NEW
rdflib>=7.0.0              # RDF/OWL processing
anthropic>=0.40.0          # LLM (optional)        ← NEW
```

## Performance Notes

**Topic Classification (Keyword mode):**
- ~50ms per article (no API calls)
- Processes 1000 articles in ~50 seconds

**Schema Subsetting:**
- Load gist: ~500ms (one-time)
- Subset generation: ~10ms per query
- Can cache subsets per topic combination

**Total pipeline (topic + schema):**
- ~60ms per article (excluding LLM extraction)

## Next Session Plan

1. Build entity extraction engine
2. Test on sample articles
3. Evaluate extraction quality
4. Iterate on prompt engineering
5. Add batch processing with progress tracking

## Questions for Next Time

1. Do you have a preference for LLM model? (Haiku for speed vs Sonnet for quality)
2. Should we build the review interface early, or focus on extraction quality first?
3. Any specific entity types you want to prioritize? (Organizations? Celestial objects? Missions?)
