# Quick Start: Classify All Articles

This guide shows how to classify all your Universe Today articles by topic.

## Step 1: Classify All Articles

### Basic Usage (Fast, No API Needed)

```bash
# Classify all articles using keyword classifier
python classify_all_articles.py
```

This will:
- Process all articles in `articles/` directory
- Use fast keyword-based classification (~50ms per article)
- Save results to `article_topics.json`
- Show progress every 10 articles

**Expected time:** ~25 minutes for 30K articles

### With Progress Tracking

The script shows real-time progress:
```
Processing 30000 articles...
Output: article_topics.json
======================================================================
[10/30000] articles_100000-galaxies...                    (15.2/sec, ~1973s remaining)
[100/30000] articles_1-2-billion-years-ago...             (18.5/sec, ~1621s remaining)
```

### Advanced Options

```bash
# Process only first 1000 articles (for testing)
python classify_all_articles.py --limit 1000

# Use higher confidence threshold (fewer topics per article)
python classify_all_articles.py --min-confidence 0.2

# Save to custom file
python classify_all_articles.py --output my_topics.json

# Resume if interrupted (replace with last article ID shown)
python classify_all_articles.py --resume articles_some-article-name
```

## Step 2: Explore the Results

### View Summary

```bash
python explore_topics.py summary
```

Output:
```
======================================================================
Topic Classification Summary
======================================================================
Total articles:    30000
Generated at:      2025-12-14T12:34:56

Topic Distribution:
----------------------------------------------------------------------
  time            25834 (86.1%) ████████████████████████████████████████████
  geo             24521 (81.7%) █████████████████████████████████████████
  content         22456 (74.9%) ███████████████████████████████████████
  events          21234 (70.8%) ███████████████████████████████████
  organizations   18543 (61.8%) ███████████████████████████████
  ...
```

### Find Articles by Topic

```bash
# Show top 20 articles about organizations
python explore_topics.py topic organizations --limit 20

# Show articles about events
python explore_topics.py topic events --limit 50
```

### Interactive Mode

```bash
python explore_topics.py interactive
```

This opens an interactive prompt where you can explore different views.

## Step 3: Export by Topic

```bash
# Export articles grouped by primary topic
python explore_topics.py export --output-dir topics/
```

Creates files like:
```
topics/
  ├── events.json       (8,234 articles)
  ├── organizations.json (5,432 articles)
  ├── geo.json          (4,123 articles)
  └── ...
```

Each file contains articles where that topic had the highest confidence.

## Step 4: Use Results in Extraction

The classification results feed into entity extraction:

```python
from classify_all_articles import load_classifications
from gist_schema import GistSchema

# Load classifications
classifications = load_classifications("article_topics.json")

# Get a specific article's topics
article = classifications["articles_james-webb-discovers-exoplanet"]
topics = article["topics"]  # e.g., ["events", "geo", "artifacts"]

# Generate schema subset for extraction
schema = GistSchema("gistCore.ttl")
subset = schema.subset_by_topics(topics)

# Use in extraction prompt...
```

## Common Workflows

### Test on Sample First

```bash
# Test on 100 articles
python classify_all_articles.py --limit 100

# Check results
python explore_topics.py summary

# If good, run on all
python classify_all_articles.py
```

### Resume After Interruption

If classification is interrupted (Ctrl+C):

```bash
# The last article ID is shown in output
python classify_all_articles.py --resume articles_last-article-id
```

Results are saved every 100 articles, so you won't lose much progress.

### Use LLM Classifier (More Accurate)

```bash
# Set API key
export ANTHROPIC_API_KEY=your-key-here

# Use LLM classifier (slower but more accurate)
python classify_all_articles.py --classifier llm --min-confidence 0.6

# Or hybrid (keyword filter, then LLM on matches)
python classify_all_articles.py --classifier hybrid
```

**Note:** LLM classifier is much slower (~2-3 seconds per article) and costs money. For 30K articles, keyword classifier is recommended unless you need maximum accuracy.

## Output Format

The `article_topics.json` file has this structure:

```json
{
  "generated_at": "2025-12-14T12:34:56",
  "total_articles": 30000,
  "topic_distribution": {
    "events": 21234,
    "time": 25834,
    ...
  },
  "articles": [
    {
      "article_id": "articles_james-webb-discovers-exoplanet",
      "file": "articles_james-webb-discovers-exoplanet.html",
      "topics": ["events", "geo", "artifacts", "organizations"],
      "confidence": {
        "events": 0.85,
        "geo": 0.72,
        "artifacts": 0.45,
        "organizations": 0.63
      },
      "method": "keyword",
      "classified_at": "2025-12-14T12:35:01"
    },
    ...
  ]
}
```

## Performance Tips

1. **Use keyword classifier for initial pass** - Fast and good enough for most articles
2. **Process in batches** - Use `--limit` to test on subsets first
3. **Results saved periodically** - Every 100 articles, so interruptions are safe
4. **Resume capability** - Can pick up where you left off

## Troubleshooting

### No articles found
```bash
# Check articles directory
ls articles/articles_*.html | head

# Specify custom directory
python classify_all_articles.py --articles-dir /path/to/articles
```

### Low confidence (too few topics)
```bash
# Lower threshold
python classify_all_articles.py --min-confidence 0.05
```

### Too many topics per article
```bash
# Raise threshold
python classify_all_articles.py --min-confidence 0.2
```

### Want to re-classify
```bash
# Just run again, it will overwrite
python classify_all_articles.py --output article_topics.json
```

## Next Steps

After classification:

1. **Explore results** - Use `explore_topics.py` to understand the distribution
2. **Build entity extraction** - Use topic-based schema subsets for targeted extraction
3. **Create domain ontology** - Identify common entity types to formalize as gist subclasses

See [PIPELINE.md](PIPELINE.md) for the full architecture.
