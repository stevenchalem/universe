#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch classify all articles in the corpus.
Saves results to JSON for later use in entity extraction.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Optional, Dict, List
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from topic_classifier import KeywordTopicClassifier, LLMTopicClassifier, HybridTopicClassifier


def classify_all_articles(
    articles_dir: Path = Path("articles"),
    output_file: Path = Path("article_topics.json"),
    classifier_type: str = "keyword",
    min_confidence: float = 0.1,
    limit: Optional[int] = None,
    resume_from: Optional[str] = None
):
    """
    Classify all articles and save topic assignments.

    Args:
        articles_dir: Directory containing article HTML files
        output_file: Where to save results (JSON)
        classifier_type: "keyword", "llm", or "hybrid"
        min_confidence: Minimum confidence threshold
        limit: Max articles to process (None = all)
        resume_from: Resume from this article ID (useful if interrupted)

    Returns:
        Dict with results and statistics
    """

    # Create classifier
    if classifier_type == "keyword":
        classifier = KeywordTopicClassifier(min_confidence=min_confidence)
        print(f"Using KeywordTopicClassifier (threshold: {min_confidence})")
    elif classifier_type == "llm":
        try:
            classifier = LLMTopicClassifier(min_confidence=min_confidence)
            print(f"Using LLMTopicClassifier (threshold: {min_confidence})")
        except Exception as e:
            print(f"Error: LLM classifier failed: {e}")
            print("Falling back to KeywordTopicClassifier")
            classifier = KeywordTopicClassifier(min_confidence=min_confidence)
    elif classifier_type == "hybrid":
        try:
            classifier = HybridTopicClassifier(
                keyword_threshold=min_confidence / 2,
                llm_threshold=min_confidence
            )
            print(f"Using HybridTopicClassifier (LLM threshold: {min_confidence})")
        except Exception as e:
            print(f"Error: Hybrid classifier failed: {e}")
            print("Falling back to KeywordTopicClassifier")
            classifier = KeywordTopicClassifier(min_confidence=min_confidence)
    else:
        raise ValueError(f"Unknown classifier type: {classifier_type}")

    # Find all article HTML files
    html_files = sorted(articles_dir.glob("articles_*.html"))

    if not html_files:
        print(f"No article files found in {articles_dir}")
        return None

    # Load existing results if resuming
    results = {}
    if resume_from and output_file.exists():
        print(f"Loading existing results from {output_file}...")
        with open(output_file, 'r') as f:
            data = json.load(f)
            results = {r["article_id"]: r for r in data.get("articles", [])}
        print(f"Loaded {len(results)} existing classifications")

    # Filter to only new articles if resuming
    if resume_from:
        found_resume = False
        filtered_files = []
        for f in html_files:
            article_id = f.stem
            if article_id == resume_from:
                found_resume = True
            if found_resume and article_id not in results:
                filtered_files.append(f)
        html_files = filtered_files
        print(f"Resuming from {resume_from}, {len(html_files)} articles to process")

    # Apply limit
    if limit:
        html_files = html_files[:limit]

    total = len(html_files)
    print(f"\nProcessing {total} articles...")
    print(f"Output: {output_file}")
    print("=" * 70)

    # Process articles
    topic_counts = {}
    errors = []
    start_time = datetime.now()

    for i, article_file in enumerate(html_files, 1):
        article_id = article_file.stem

        # Progress indicator
        if i % 10 == 0 or i == 1:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            remaining = (total - i) / rate if rate > 0 else 0
            print(f"[{i}/{total}] {article_id[:50]:<50s} ({rate:.1f}/sec, ~{remaining:.0f}s remaining)")

        try:
            # Read article
            with open(article_file, 'r', encoding='utf-8') as f:
                html = f.read()

            # Classify
            classification = classifier.classify(html, article_id=article_id)

            # Store result
            results[article_id] = {
                "article_id": article_id,
                "file": article_file.name,
                "topics": classification.topics,
                "confidence": classification.confidence,
                "method": classification.method,
                "classified_at": datetime.now().isoformat()
            }

            # Update topic counts
            for topic in classification.topics:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

            # Save periodically (every 100 articles)
            if i % 100 == 0:
                _save_results(output_file, results, start_time, topic_counts)

        except Exception as e:
            error_msg = f"{article_file.name}: {str(e)}"
            errors.append(error_msg)
            print(f"  ERROR: {error_msg}")

    # Final save
    _save_results(output_file, results, start_time, topic_counts, errors)

    # Print summary
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 70)
    print("Classification Complete!")
    print("=" * 70)
    print(f"Total articles:     {len(results)}")
    print(f"Time elapsed:       {elapsed:.1f}s ({len(results)/elapsed:.1f} articles/sec)")
    print(f"Errors:             {len(errors)}")
    print(f"Output saved to:    {output_file}")

    if topic_counts:
        print(f"\nTopic Distribution:")
        print("-" * 70)
        for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(results)) * 100
            bar = "█" * int(pct / 2)
            print(f"  {topic:15s} {count:5d} ({pct:5.1f}%) {bar}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    return {
        "total": len(results),
        "elapsed": elapsed,
        "errors": len(errors),
        "topic_counts": topic_counts
    }


def _save_results(output_file: Path, results: Dict, start_time: datetime,
                  topic_counts: Dict, errors: List[str] = None):
    """Save results to JSON file."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "started_at": start_time.isoformat(),
        "total_articles": len(results),
        "topic_distribution": topic_counts,
        "errors": errors or [],
        "articles": list(results.values())
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)


def load_classifications(file_path: Path = Path("article_topics.json")) -> Dict:
    """
    Load previously saved classifications.

    Returns:
        Dict mapping article_id -> classification data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    return {
        article["article_id"]: article
        for article in data.get("articles", [])
    }


def get_articles_by_topic(topic: str,
                          classifications_file: Path = Path("article_topics.json")) -> List[Dict]:
    """
    Get all articles classified with a specific topic.

    Args:
        topic: Topic name (e.g., "events", "organizations")
        classifications_file: Path to classifications JSON

    Returns:
        List of article classifications containing the topic
    """
    classifications = load_classifications(classifications_file)

    return [
        article for article in classifications.values()
        if topic in article.get("topics", [])
    ]


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch classify all articles by topic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Classify all articles with keyword classifier
  python classify_all_articles.py

  # Use LLM classifier (requires Anthropic API key)
  python classify_all_articles.py --classifier llm

  # Process first 100 articles only
  python classify_all_articles.py --limit 100

  # Resume from a specific article
  python classify_all_articles.py --resume articles_some-article

  # More strict confidence threshold
  python classify_all_articles.py --min-confidence 0.2

  # Custom output file
  python classify_all_articles.py --output my_topics.json
        """
    )

    parser.add_argument(
        "--articles-dir",
        type=Path,
        default=Path("articles"),
        help="Directory containing article HTML files (default: articles/)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("article_topics.json"),
        help="Output JSON file (default: article_topics.json)"
    )
    parser.add_argument(
        "--classifier",
        choices=["keyword", "llm", "hybrid"],
        default="keyword",
        help="Classifier type (default: keyword)"
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.1,
        help="Minimum confidence threshold (default: 0.1)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Max articles to process (default: all)"
    )
    parser.add_argument(
        "--resume",
        type=str,
        help="Resume from this article ID"
    )

    args = parser.parse_args()

    # Check articles directory exists
    if not args.articles_dir.exists():
        print(f"Error: Articles directory not found: {args.articles_dir}")
        sys.exit(1)

    # Run classification
    try:
        classify_all_articles(
            articles_dir=args.articles_dir,
            output_file=args.output,
            classifier_type=args.classifier,
            min_confidence=args.min_confidence,
            limit=args.limit,
            resume_from=args.resume
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Partial results saved.")
        print(f"To resume, run: python classify_all_articles.py --resume <last-article-id>")
        sys.exit(1)


if __name__ == "__main__":
    main()
