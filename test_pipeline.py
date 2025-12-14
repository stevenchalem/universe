#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick validation tests for the KG pipeline components.
Run this to verify everything is working.
"""

from pathlib import Path
import sys
import os

# Fix Windows console encoding for Unicode
if sys.platform == "win32":
    os.system("chcp 65001 >nul 2>&1")
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


def test_gist_schema():
    """Test gist schema loading and subsetting."""
    print("Testing gist_schema.py...")

    try:
        from gist_schema import GistSchema, available_topics

        topics = available_topics()
        assert len(topics) == 11, f"Expected 11 topics, got {len(topics)}"
        assert "events" in topics
        assert "organizations" in topics
        print(f"  ✓ Topic seeds defined: {', '.join(topics)}")

        # Try to load schema (will fail if TTL not present, that's okay)
        gist_files = [
            "gistCore14_0_0.ttl",
            "gistCore.ttl",
            "/mnt/user-data/uploads/gistCore14_0_0.ttl"
        ]

        gist_path = None
        for path in gist_files:
            if Path(path).exists():
                gist_path = path
                break

        if gist_path:
            schema = GistSchema(gist_path)
            assert len(schema.classes) > 50, "Should have loaded 50+ classes"
            assert len(schema.properties) > 50, "Should have loaded 50+ properties"

            # Test subsetting
            subset = schema.subset_by_topics(["events", "time"])
            stats = subset.stats()
            assert stats["classes"] > 0
            assert stats["object_properties"] > 0

            print(f"  ✓ Loaded {len(schema.classes)} classes, {len(schema.properties)} properties")
            print(f"  ✓ Subset for ['events', 'time']: {stats['classes']} classes, "
                  f"{stats['object_properties']} obj props, {stats['datatype_properties']} data props")

            # Test prompt generation
            prompt = subset.to_prompt_text(max_definition_len=80)
            assert len(prompt) > 100
            assert "gist:" in prompt
            print(f"  ✓ Generated {len(prompt)} char extraction prompt")
        else:
            print("  ⚠ gistCore.ttl not found - skipping schema tests")
            print("    Download from: https://www.semanticarts.com/gist/")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

    return True


def test_topic_classifier():
    """Test topic classification."""
    print("\nTesting topic_classifier.py...")

    try:
        from topic_classifier import KeywordTopicClassifier, classify_article_file

        # Test on sample text
        sample = """
        NASA's James Webb Space Telescope has discovered a new exoplanet
        orbiting a distant star. The planet, located 400 light-years from Earth,
        appears to have water vapor in its atmosphere. The discovery was made
        on January 15, 2024, by an international team of astronomers.
        """

        classifier = KeywordTopicClassifier(min_confidence=0.05)
        result = classifier.classify(sample)

        assert len(result.topics) > 0, "Should detect at least one topic"
        assert "organizations" in result.topics, "Should detect 'organizations' (NASA)"
        assert "geo" in result.topics or "categories" in result.topics, "Should detect geo/categories"
        assert result.method == "keyword"

        print(f"  ✓ Classified sample text: {result.topics}")
        print(f"  ✓ Confidence scores: {list(result.confidence.keys())[:3]}")

        # Test on real article if available
        articles_dir = Path("articles")
        if articles_dir.exists():
            html_files = list(articles_dir.glob("articles_*.html"))
            if html_files:
                result = classify_article_file(html_files[0], classifier)
                assert len(result.topics) > 0
                print(f"  ✓ Classified article file: {html_files[0].name}")
                print(f"    Topics: {', '.join(result.topics[:5])}")
            else:
                print("  ⚠ No article HTML files found")
        else:
            print("  ⚠ No articles/ directory found")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_integration():
    """Test full pipeline integration."""
    print("\nTesting integration...")

    try:
        from topic_classifier import KeywordTopicClassifier
        from gist_schema import GistSchema

        # Find gist file
        gist_path = None
        for candidate in ["gistCore14_0_0.ttl", "gistCore.ttl", "/mnt/user-data/uploads/gistCore14_0_0.ttl"]:
            if Path(candidate).exists():
                gist_path = candidate
                break

        if not gist_path:
            print("  ⚠ Skipping integration test (no gistCore.ttl)")
            return True

        # Sample article
        sample = """
        SpaceX successfully launched a Falcon 9 rocket carrying 52 Starlink satellites
        from Cape Canaveral on March 10, 2024. The first stage booster landed on the
        drone ship in the Atlantic Ocean nine minutes after liftoff.
        """

        # Classify
        classifier = KeywordTopicClassifier(min_confidence=0.1)
        classification = classifier.classify(sample)

        # Subset
        schema = GistSchema(gist_path)
        subset = schema.subset_by_topics(classification.topics)

        # Generate prompt
        prompt = subset.to_prompt_text(max_definition_len=80)

        assert len(classification.topics) > 0
        assert subset.stats()["classes"] > 0
        assert len(prompt) > 100

        print(f"  ✓ End-to-end: {len(classification.topics)} topics → "
              f"{subset.stats()['classes']} classes → {len(prompt)} char prompt")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def test_dependencies():
    """Check required dependencies."""
    print("\nChecking dependencies...")

    required = {
        "beautifulsoup4": "bs4",
        "rdflib": "rdflib"
    }

    optional = {
        "anthropic": "anthropic"
    }

    all_good = True

    for pkg_name, import_name in required.items():
        try:
            __import__(import_name)
            print(f"  ✓ {pkg_name}")
        except ImportError:
            print(f"  ✗ {pkg_name} - REQUIRED")
            all_good = False

    for pkg_name, import_name in optional.items():
        try:
            __import__(import_name)
            print(f"  ✓ {pkg_name} (optional)")
        except ImportError:
            print(f"  ⚠ {pkg_name} - optional (for LLM classification)")

    if not all_good:
        print("\nInstall missing packages:")
        print("  pip install -r requirements.txt")

    return all_good


def main():
    """Run all tests."""
    print("=" * 70)
    print("KG Pipeline Validation Tests")
    print("=" * 70)

    results = []

    results.append(("Dependencies", test_dependencies()))
    results.append(("gist_schema.py", test_gist_schema()))
    results.append(("topic_classifier.py", test_topic_classifier()))
    results.append(("Integration", test_integration()))

    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8s} {name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Pipeline ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
