#!/usr/bin/env python3
"""
Explore and analyze topic classification results.
"""

from pathlib import Path
import json
from collections import defaultdict
from typing import List, Dict, Optional
import sys


def load_results(file_path: Path = Path("article_topics.json")) -> Dict:
    """Load classification results."""
    with open(file_path, 'r') as f:
        return json.load(f)


def show_summary(results: Dict):
    """Show summary statistics."""
    print("=" * 70)
    print("Topic Classification Summary")
    print("=" * 70)
    print(f"Total articles:    {results['total_articles']}")
    print(f"Generated at:      {results['generated_at']}")
    print(f"Errors:            {len(results.get('errors', []))}")

    print(f"\nTopic Distribution:")
    print("-" * 70)
    topic_dist = results.get('topic_distribution', {})
    total = results['total_articles']

    for topic, count in sorted(topic_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        bar = "█" * int(pct / 2)
        print(f"  {topic:15s} {count:5d} ({pct:5.1f}%) {bar}")


def show_topic_combinations(results: Dict, top_n: int = 20):
    """Show most common topic combinations."""
    print(f"\nTop {top_n} Topic Combinations:")
    print("-" * 70)

    combos = defaultdict(int)
    for article in results['articles']:
        topics = tuple(sorted(article['topics']))
        combos[topics] += 1

    for topics, count in sorted(combos.items(), key=lambda x: x[1], reverse=True)[:top_n]:
        pct = (count / results['total_articles']) * 100
        topics_str = ", ".join(topics) if topics else "(none)"
        print(f"  {count:4d} ({pct:4.1f}%) {topics_str}")


def show_articles_for_topic(results: Dict, topic: str, limit: int = 10):
    """Show sample articles for a specific topic."""
    print(f"\nSample Articles for Topic: {topic}")
    print("-" * 70)

    articles = [
        a for a in results['articles']
        if topic in a.get('topics', [])
    ]

    # Sort by confidence in this topic
    articles.sort(
        key=lambda a: a.get('confidence', {}).get(topic, 0),
        reverse=True
    )

    if not articles:
        print(f"  No articles found for topic: {topic}")
        return

    print(f"  Found {len(articles)} articles")
    print(f"  Showing top {min(limit, len(articles))} by confidence:\n")

    for i, article in enumerate(articles[:limit], 1):
        conf = article.get('confidence', {}).get(topic, 0)
        article_id = article['article_id'].replace('articles_', '').replace('.html', '')
        # Truncate long IDs
        if len(article_id) > 60:
            article_id = article_id[:57] + "..."
        print(f"  {i:2d}. [{conf:.2f}] {article_id}")


def find_low_coverage_articles(results: Dict, max_topics: int = 2, limit: int = 20):
    """Find articles with few topics (might need manual review)."""
    print(f"\nArticles with ≤{max_topics} Topics (Low Coverage):")
    print("-" * 70)

    low_coverage = [
        a for a in results['articles']
        if len(a.get('topics', [])) <= max_topics
    ]

    # Sort by topic count
    low_coverage.sort(key=lambda a: len(a.get('topics', [])))

    if not low_coverage:
        print(f"  No articles with ≤{max_topics} topics")
        return

    print(f"  Found {len(low_coverage)} articles")
    print(f"  Showing first {min(limit, len(low_coverage))}:\n")

    for i, article in enumerate(low_coverage[:limit], 1):
        topics = article.get('topics', [])
        article_id = article['article_id'].replace('articles_', '').replace('.html', '')
        if len(article_id) > 50:
            article_id = article_id[:47] + "..."
        topics_str = ", ".join(topics) if topics else "(none)"
        print(f"  {i:2d}. [{len(topics)} topics] {article_id}")
        print(f"      → {topics_str}")


def export_by_topic(results: Dict, output_dir: Path = Path("topics_by_category")):
    """Export articles grouped by primary topic to separate files."""
    output_dir.mkdir(exist_ok=True)

    # Group by primary topic (highest confidence)
    by_topic = defaultdict(list)

    for article in results['articles']:
        if not article.get('topics'):
            by_topic['unclassified'].append(article)
            continue

        # Find topic with highest confidence
        confidences = article.get('confidence', {})
        primary = max(article['topics'], key=lambda t: confidences.get(t, 0))
        by_topic[primary].append(article)

    print(f"\nExporting to {output_dir}/")
    print("-" * 70)

    for topic, articles in sorted(by_topic.items()):
        output_file = output_dir / f"{topic}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "topic": topic,
                "count": len(articles),
                "articles": articles
            }, f, indent=2)
        print(f"  {topic:15s} → {output_file.name:25s} ({len(articles):4d} articles)")

    print(f"\nExported {len(by_topic)} topic files to {output_dir}/")


def interactive_explore(results: Dict):
    """Interactive exploration mode."""
    print("\n" + "=" * 70)
    print("Interactive Topic Explorer")
    print("=" * 70)

    topics = sorted(results.get('topic_distribution', {}).keys())

    while True:
        print("\nCommands:")
        print("  1. Show summary")
        print("  2. Show topic combinations")
        print("  3. Show articles for topic")
        print("  4. Find low coverage articles")
        print("  5. Export by topic")
        print("  q. Quit")

        choice = input("\nEnter choice: ").strip().lower()

        if choice == 'q':
            break
        elif choice == '1':
            show_summary(results)
        elif choice == '2':
            n = input("How many? [20]: ").strip() or "20"
            show_topic_combinations(results, int(n))
        elif choice == '3':
            print(f"\nAvailable topics: {', '.join(topics)}")
            topic = input("Topic name: ").strip()
            if topic in topics:
                limit = input("How many articles? [10]: ").strip() or "10"
                show_articles_for_topic(results, topic, int(limit))
            else:
                print(f"Unknown topic: {topic}")
        elif choice == '4':
            max_t = input("Max topics? [2]: ").strip() or "2"
            find_low_coverage_articles(results, int(max_t))
        elif choice == '5':
            export_by_topic(results)
        else:
            print("Unknown command")


def main():
    """Command-line interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Explore topic classification results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show summary
  python explore_topics.py summary

  # Show top topic combinations
  python explore_topics.py combinations --top 30

  # Show articles for a topic
  python explore_topics.py topic events --limit 20

  # Find low coverage articles
  python explore_topics.py low-coverage --max-topics 1

  # Export articles by topic
  python explore_topics.py export --output-dir topics/

  # Interactive mode
  python explore_topics.py interactive
        """
    )

    parser.add_argument(
        "command",
        choices=["summary", "combinations", "topic", "low-coverage", "export", "interactive"],
        help="Command to run"
    )
    parser.add_argument(
        "topic_name",
        nargs='?',
        help="Topic name (for 'topic' command)"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("article_topics.json"),
        help="Input classification file (default: article_topics.json)"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of items to show (default: 20)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Limit for article lists (default: 10)"
    )
    parser.add_argument(
        "--max-topics",
        type=int,
        default=2,
        help="Max topics for low-coverage (default: 2)"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("topics_by_category"),
        help="Output directory for export (default: topics_by_category/)"
    )

    args = parser.parse_args()

    # Load results
    if not args.input.exists():
        print(f"Error: Classification file not found: {args.input}")
        print("Run 'python classify_all_articles.py' first")
        sys.exit(1)

    results = load_results(args.input)

    # Execute command
    if args.command == "summary":
        show_summary(results)
    elif args.command == "combinations":
        show_topic_combinations(results, args.top)
    elif args.command == "topic":
        if not args.topic_name:
            print("Error: topic name required")
            print(f"Available: {', '.join(results['topic_distribution'].keys())}")
            sys.exit(1)
        show_articles_for_topic(results, args.topic_name, args.limit)
    elif args.command == "low-coverage":
        find_low_coverage_articles(results, args.max_topics, args.limit)
    elif args.command == "export":
        export_by_topic(results, args.output_dir)
    elif args.command == "interactive":
        interactive_explore(results)


if __name__ == "__main__":
    main()
