# Universe Today Knowledge Graph Experiment

This is an experiment directed toward building an open-standards knowledge graph based on the content at [www.universetoday.com](https://universetoday.com). I am not affiliated with Universe Today except as a member of their Patreon channel.

I am using Universe Today content per its [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Test the pipeline
python test_pipeline.py

# Classify sample articles
python topic_classifier.py

# Run full demo (requires gistCore.ttl)
python pipeline_demo.py
```

## Project Structure

- **[PIPELINE.md](PIPELINE.md)** - Full architecture and pipeline documentation
- **[STATUS.md](STATUS.md)** - Current progress and next steps
- **[gist_schema.py](gist_schema.py)** - Schema loading and subsetting
- **[topic_classifier.py](topic_classifier.py)** - Article topic classification
- **[pipeline_demo.py](pipeline_demo.py)** - End-to-end demonstration
- **[test_pipeline.py](test_pipeline.py)** - Validation tests
- **[download_articles.py](download_articles.md)** - Article scraper ([docs](download_articles.md))

## What's Working

✅ Topic classification (keyword + LLM modes)
✅ Schema subsetting from gist ontology
✅ Pipeline integration
🚧 Entity extraction (next step)
🚧 Relationship extraction
🚧 Entity resolution
🚧 Review interface

See [STATUS.md](STATUS.md) for details.
