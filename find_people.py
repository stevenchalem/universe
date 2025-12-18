#!/usr/bin/env python3
"""
Find person names mentioned in articles.
"""

import re
from pathlib import Path
from collections import Counter
from bs4 import BeautifulSoup


def extract_people_mentions(articles_dir: Path = Path("articles"), limit: int = 1000):
    """
    Extract potential person names from articles.
    Uses simple heuristics: capitalized words that appear in common contexts.
    """

    # Common patterns for people mentions
    people_patterns = [
        # Author bylines
        r'\bby\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        # Dr./Professor/etc
        r'\b(?:Dr\.|Prof\.|Professor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        # Said/told patterns
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:said|told|explained|noted|added|stated)',
        # According to
        r'\baccording to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        # Led by / directed by
        r'\b(?:led|directed|headed)\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        # Researcher/scientist patterns
        r'\b(?:researcher|scientist|astronomer|physicist)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]

    name_counter = Counter()
    html_files = list(articles_dir.glob("articles_*.html"))[:limit]

    print(f"Scanning {len(html_files)} articles for person names...")

    for i, article_file in enumerate(html_files, 1):
        if i % 100 == 0:
            print(f"  Processed {i}/{len(html_files)} articles...")

        try:
            with open(article_file, 'r', encoding='utf-8') as f:
                html = f.read()

            # Extract text from HTML
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            text = soup.get_text()

            # Find names using all patterns
            for pattern in people_patterns:
                matches = re.findall(pattern, text)
                for name in matches:
                    # Clean up the name
                    name = name.strip()
                    # Filter out common false positives
                    if (len(name) > 3 and
                        not any(word in name.lower() for word in
                               ['universe today', 'nasa', 'spacex', 'mars', 'earth',
                                'jupiter', 'saturn', 'venus', 'mercury', 'neptune',
                                'pluto', 'uranus', 'european space', 'space agency'])):
                        name_counter[name] += 1

        except Exception as e:
            print(f"Error processing {article_file.name}: {e}")

    return name_counter


def main():
    print("Extracting person names from articles...\n")

    names = extract_people_mentions(limit=5000)

    print("\n" + "=" * 70)
    print(f"Found {len(names)} unique names")
    print("=" * 70)

    print("\nTop 100 most mentioned people:")
    for i, (name, count) in enumerate(names.most_common(100), 1):
        print(f"{i:3d}. {name:40s} {count:5d} mentions")

    # Save results
    import json
    output_file = Path("people_mentions.json")
    data = {
        "total_unique_names": len(names),
        "top_500": [
            {"name": name, "count": count}
            for name, count in names.most_common(500)
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
