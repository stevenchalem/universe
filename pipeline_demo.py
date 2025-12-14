#!/usr/bin/env python3
"""
Demo of the KG population pipeline: topic classification → schema subsetting
"""

from pathlib import Path
import json
from topic_classifier import KeywordTopicClassifier, classify_article_file
from gist_schema import GistSchema


def demo_pipeline(article_path: Path, gist_ontology_path: str):
    """
    Demonstrate full pipeline from article to schema subset.

    Args:
        article_path: Path to article HTML file
        gist_ontology_path: Path to gistCore TTL file
    """
    print("=" * 70)
    print(f"Processing: {article_path.name}")
    print("=" * 70)

    # Step 1: Classify article topics
    print("\n[1] Topic Classification")
    print("-" * 70)

    classifier = KeywordTopicClassifier(min_confidence=0.1)
    classification = classify_article_file(article_path, classifier)

    print(f"Identified topics: {', '.join(classification.topics)}")
    print(f"\nConfidence scores:")
    for topic in classification.topics:
        conf = classification.confidence.get(topic, 0)
        bar = "█" * int(conf * 50)
        print(f"  {topic:15s} {conf:5.2f} {bar}")

    # Step 2: Load gist schema and create subset
    print(f"\n[2] Schema Subsetting")
    print("-" * 70)

    schema = GistSchema(gist_ontology_path)
    subset = schema.subset_by_topics(classification.topics)

    stats = subset.stats()
    print(f"Schema subset contains:")
    print(f"  Classes:             {stats['classes']}")
    print(f"  Object Properties:   {stats['object_properties']}")
    print(f"  Datatype Properties: {stats['datatype_properties']}")

    # Step 3: Generate extraction prompt
    print(f"\n[3] Extraction Prompt Preview")
    print("-" * 70)

    schema_text = subset.to_prompt_text(max_definition_len=80)
    lines = schema_text.split('\n')

    # Show first 50 lines
    preview = '\n'.join(lines[:50])
    print(preview)

    if len(lines) > 50:
        print(f"\n... ({len(lines) - 50} more lines)")

    print(f"\n[4] Next Steps")
    print("-" * 70)
    print("This schema subset can now be used in:")
    print("  • Entity extraction prompts (with article text)")
    print("  • Relationship extraction prompts (with extracted entities)")
    print("  • Schema bootstrapping (proposing new domain subclasses)")
    print()

    return classification, subset, schema_text


def batch_classify_articles(articles_dir: Path, output_file: Path, limit: int = 100):
    """
    Classify multiple articles and save results.

    Args:
        articles_dir: Directory containing article HTML files
        output_file: Where to save classification results (JSON)
        limit: Max articles to process
    """
    classifier = KeywordTopicClassifier(min_confidence=0.1)

    html_files = list(articles_dir.glob("articles_*.html"))[:limit]

    results = []
    print(f"Classifying {len(html_files)} articles...")

    for i, article_file in enumerate(html_files, 1):
        if i % 10 == 0:
            print(f"  Processed {i}/{len(html_files)}...")

        classification = classify_article_file(article_file, classifier)

        results.append({
            "article": article_file.name,
            "topics": classification.topics,
            "confidence": classification.confidence
        })

    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nSaved classifications to {output_file}")

    # Print topic distribution
    topic_counts = {}
    for result in results:
        for topic in result["topics"]:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

    print("\nTopic distribution:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        pct = (count / len(results)) * 100
        print(f"  {topic:15s} {count:4d} ({pct:5.1f}%)")


def main():
    """Run pipeline demo."""
    import sys

    # Check for gist ontology
    gist_path = None
    for candidate in ["gistCore14_0_0.ttl", "gistCore.ttl", "/mnt/user-data/uploads/gistCore14_0_0.ttl"]:
        if Path(candidate).exists():
            gist_path = candidate
            break

    if not gist_path:
        print("ERROR: gistCore ontology file not found.")
        print("Please download from https://www.semanticarts.com/gist/")
        print("Or provide path as first argument: python pipeline_demo.py <path-to-gist.ttl>")
        return

    if len(sys.argv) > 1:
        gist_path = sys.argv[1]

    # Find sample article
    articles_dir = Path("articles")
    if not articles_dir.exists():
        print("No articles directory found")
        return

    html_files = list(articles_dir.glob("articles_*.html"))
    if not html_files:
        print("No article HTML files found")
        return

    # Demo on first article
    sample_article = html_files[0]
    classification, subset, schema_text = demo_pipeline(sample_article, gist_path)

    # Save schema subset for inspection
    output_file = Path("schema_subset_sample.txt")
    with open(output_file, 'w') as f:
        f.write(schema_text)
    print(f"\nFull schema subset saved to: {output_file}")

    # Optionally batch process
    print("\n" + "=" * 70)
    response = input("\nBatch classify more articles? (y/n): ")
    if response.lower() == 'y':
        batch_classify_articles(
            articles_dir,
            Path("article_classifications.json"),
            limit=100
        )


if __name__ == "__main__":
    main()
