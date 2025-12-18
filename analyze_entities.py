#!/usr/bin/env python3
"""
Analyze unique entities/terms found across all articles.
"""

import json
import re
from pathlib import Path
from collections import Counter
from topic_classifier import KeywordTopicClassifier


def extract_unique_matches(articles_dir: Path = Path("articles")):
    """
    Extract all unique entity matches from articles.

    Returns:
        Dict mapping topic -> Counter of matched terms
    """
    classifier = KeywordTopicClassifier(min_confidence=0.05)

    # Track all matches per topic
    topic_matches = {topic: Counter() for topic in classifier.patterns.keys()}

    html_files = list(articles_dir.glob("articles_*.html"))
    print(f"Analyzing {len(html_files)} articles...")

    for i, article_file in enumerate(html_files, 1):
        if i % 1000 == 0:
            print(f"  Processed {i}/{len(html_files)} articles...")

        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                html = f.read()

            # Clean text
            text = classifier._clean_text(html)

            # Find all matches per topic
            for topic, pattern in classifier.patterns.items():
                matches = pattern.findall(text.lower())
                for match in matches:
                    # Extract the actual matched text (not the groups)
                    if isinstance(match, tuple):
                        match = next((m for m in match if m), '')
                    if match:
                        topic_matches[topic][match] += 1

        except Exception as e:
            print(f"Error processing {article_file.name}: {e}")

    return topic_matches


def main():
    print("Extracting unique entities from all articles...\n")

    topic_matches = extract_unique_matches()

    # Print summary
    print("\n" + "=" * 70)
    print("UNIQUE ENTITY ANALYSIS")
    print("=" * 70)

    total_unique = 0
    for topic in sorted(topic_matches.keys()):
        matches = topic_matches[topic]
        unique_count = len(matches)
        total_matches = sum(matches.values())
        total_unique += unique_count

        print(f"\n{topic.upper()}")
        print(f"  Unique terms: {unique_count:,}")
        print(f"  Total matches: {total_matches:,}")

        # Show top 20 most common
        print(f"  Top 20 most common:")
        for term, count in matches.most_common(20):
            print(f"    {term[:50]:50s} {count:6,} mentions")

    print("\n" + "=" * 70)
    print(f"TOTAL UNIQUE TERMS ACROSS ALL TOPICS: {total_unique:,}")
    print("=" * 70)

    # Save detailed results
    output_file = Path("entity_analysis.json")
    data = {
        topic: {
            "unique_count": len(matches),
            "total_matches": sum(matches.values()),
            "top_100": [{"term": term, "count": count}
                       for term, count in matches.most_common(100)]
        }
        for topic, matches in topic_matches.items()
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
