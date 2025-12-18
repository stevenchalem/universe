#!/usr/bin/env python3
"""
Keyword-based topic classifier for gist schema subsetting.
Fast first pass - flags articles by topic based on pattern matching.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple
from collections import Counter

# Keyword patterns per topic
# Each topic has: exact matches (case-insensitive), and regex patterns
TOPIC_KEYWORDS = {
    "organizations": {
        "exact": [
            # Space agencies
            "nasa", "esa", "jaxa", "roscosmos", "cnsa", "isro", "csa",
            "european space agency", "space force",
            # Companies
            "spacex", "blue origin", "boeing", "lockheed", "northrop",
            "rocket lab", "virgin galactic", "axiom", "sierra space",
            "united launch alliance", "ula", "arianespace",
            # Institutions
            "jpl", "jet propulsion laboratory", "caltech", "mit",
            "university", "institute", "observatory", "laboratory",
            # Generic
            "agency", "organization", "company", "corporation", "team",
            "collaboration", "consortium", "partnership",
        ],
        "patterns": [
            r"\b[A-Z]{3,5}\b",  # Acronyms like NASA, ESA (will overcount)
        ]
    },
    
    "events": {
        "exact": [
            "launch", "launched", "launching", "liftoff",
            "mission", "missions",
            "landing", "landed", "touchdown",
            "discovery", "discovered", "discovering",
            "observation", "observed", "observing", "detected",
            "flyby", "rendezvous", "docking", "undocking",
            "spacewalk", "eva",
            "test", "testing", "experiment",
            "announcement", "announced", "conference",
            "ceremony", "event",
        ],
        "patterns": []
    },
    
    "time": {
        "exact": [
            "years ago", "months ago", "days ago",
            "yesterday", "today", "tomorrow",
            "ancient", "early", "late", "recent", "recently",
            "billion years", "million years",
            "schedule", "scheduled", "timeline", "deadline",
            "duration", "period",
        ],
        "patterns": [
            r"\b(19|20)\d{2}\b",  # Years like 1969, 2024
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
            r"\d{1,2}:\d{2}\s*(am|pm|utc|est|pst|gmt)",  # Times
        ]
    },
    
    "geo": {
        "exact": [
            # Solar system
            "mercury", "venus", "earth", "mars", "jupiter", "saturn",
            "uranus", "neptune", "pluto",
            "moon", "lunar", "phobos", "deimos", "titan", "europa",
            "enceladus", "ganymede", "callisto", "io",
            "asteroid", "comet", "meteor", "meteorite",
            "sun", "solar",
            # Regions
            "crater", "valley", "mountain", "pole", "equator",
            "surface", "atmosphere", "orbit", "orbital",
            # Deep space
            "galaxy", "galaxies", "nebula", "star", "stars",
            "exoplanet", "planet", "planetary",
            "milky way", "andromeda",
            # Earth locations (for launches, observatories)
            "kennedy", "cape canaveral", "vandenberg", "baikonur",
            "kourou", "tanegashima",
        ],
        "patterns": [
            r"\b[A-Z][a-z]+-\d+[a-z]?\b",  # Designations like Kepler-452b
        ]
    },
    
    "quantities": {
        "exact": [
            "kilometer", "kilometers", "km",
            "mile", "miles", "meter", "meters",
            "light-year", "light-years", "light year", "light years",
            "astronomical unit", "au", "parsec",
            "kilogram", "kg", "ton", "tons", "pound", "pounds",
            "degree", "degrees", "celsius", "fahrenheit", "kelvin",
            "percent", "percentage",
            "million", "billion", "trillion",
            "diameter", "radius", "mass", "weight", "volume",
            "speed", "velocity", "acceleration",
            "temperature", "pressure", "density",
            "magnitude", "brightness", "luminosity",
            "distance", "altitude", "depth",
        ],
        "patterns": [
            r"\d+\.?\d*\s*(km|m|kg|lb|°|%)",  # Numbers with units
            r"\d+\.?\d*\s*(million|billion|trillion)",
        ]
    },
    
    "artifacts": {
        "exact": [
            # Spacecraft types
            "spacecraft", "satellite", "satellites", "probe", "probes",
            "rover", "rovers", "lander", "landers", "orbiter", "orbiters",
            "capsule", "module", "station",
            # Specific spacecraft
            "hubble", "webb", "jwst", "james webb",
            "perseverance", "curiosity", "opportunity", "spirit",
            "voyager", "cassini", "juno", "new horizons",
            "iss", "international space station", "tiangong",
            "starship", "falcon", "dragon", "starliner", "orion",
            "artemis", "apollo", "soyuz",
            # Instruments
            "telescope", "telescopes", "camera", "spectrometer",
            "radar", "antenna", "sensor", "detector", "instrument",
            # Rockets
            "rocket", "rockets", "booster", "engine",
            "sls", "space launch system",
        ],
        "patterns": []
    },
    
    "agreements": {
        "exact": [
            "agreement", "contract", "treaty", "deal",
            "partnership", "collaboration", "cooperation",
            "signed", "signing", "negotiation",
            "funding", "funded", "budget", "cost", "costs",
            "billion dollar", "million dollar",
            "award", "awarded", "grant",
        ],
        "patterns": [
            r"\$\d+\.?\d*\s*(million|billion|m|b)",  # Dollar amounts
        ]
    },
    
    "content": {
        "exact": [
            "paper", "study", "research", "published", "journal",
            "report", "reported", "analysis", "data",
            "image", "images", "photo", "photograph", "picture",
            "video", "footage", "animation",
            "announcement", "press release", "statement",
            "interview", "presentation",
        ],
        "patterns": []
    },
    
    "collections": {
        "exact": [
            "catalog", "catalogue", "database", "archive",
            "survey", "census", "inventory",
            "series", "sequence", "set", "collection",
            "network", "array", "constellation",
        ],
        "patterns": []
    },
    
    "categories": {
        "exact": [
            "type", "types", "category", "categories", "class",
            "classification", "classified",
            "kind", "variety", "species",
        ],
        "patterns": []
    },
    
    "intentions": {
        "exact": [
            "goal", "goals", "objective", "objectives",
            "mission", "purpose", "aim",
            "plan", "plans", "planned", "planning",
            "design", "designed", "intended",
            "requirement", "requirements", "specification",
            "target", "targeting",
        ],
        "patterns": []
    },
}

# Minimum score thresholds per topic (tune these based on results)
TOPIC_THRESHOLDS = {
    "organizations": 2,
    "events": 2,
    "time": 2,
    "geo": 3,
    "quantities": 2,
    "artifacts": 2,
    "agreements": 2,
    "content": 2,
    "collections": 2,
    "categories": 2,
    "intentions": 2,
}


@dataclass
class TopicMatch:
    """Result of topic classification for an article."""
    topics: List[str]  # Topics that passed threshold
    scores: Dict[str, int]  # Raw scores per topic
    matched_keywords: Dict[str, List[str]]  # Which keywords matched per topic
    
    def __repr__(self):
        return f"TopicMatch(topics={self.topics}, scores={self.scores})"


class TopicClassifier:
    """Keyword-based topic classifier."""
    
    def __init__(self, 
                 keywords: Dict = None, 
                 thresholds: Dict = None):
        self.keywords = keywords or TOPIC_KEYWORDS
        self.thresholds = thresholds or TOPIC_THRESHOLDS
        
        # Precompile patterns
        self._compiled_patterns = {}
        for topic, data in self.keywords.items():
            self._compiled_patterns[topic] = [
                re.compile(p, re.IGNORECASE) 
                for p in data.get("patterns", [])
            ]
    
    def classify(self, text: str) -> TopicMatch:
        """
        Classify text into topics based on keyword matches.
        
        Args:
            text: Article text to classify
            
        Returns:
            TopicMatch with topics, scores, and matched keywords
        """
        text_lower = text.lower()
        scores = {}
        matched = {}
        
        for topic, data in self.keywords.items():
            topic_matches = []
            score = 0
            
            # Check exact keywords
            for keyword in data.get("exact", []):
                # Use word boundary matching for single words
                if " " in keyword:
                    # Multi-word phrase: simple containment
                    count = text_lower.count(keyword)
                else:
                    # Single word: use regex for word boundary
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    count = len(re.findall(pattern, text_lower))
                
                if count > 0:
                    score += count
                    topic_matches.append(f"{keyword}({count})")
            
            # Check regex patterns
            for pattern in self._compiled_patterns.get(topic, []):
                matches = pattern.findall(text)
                if matches:
                    score += len(matches)
                    # Only record a sample of matches
                    sample = matches[:3]
                    topic_matches.append(f"pattern:{','.join(str(m) for m in sample)}")
            
            scores[topic] = score
            matched[topic] = topic_matches
        
        # Determine which topics pass threshold
        passing_topics = [
            topic for topic, score in scores.items()
            if score >= self.thresholds.get(topic, 2)
        ]
        
        return TopicMatch(
            topics=passing_topics,
            scores=scores,
            matched_keywords=matched
        )
    
    def classify_batch(self, texts: List[str]) -> List[TopicMatch]:
        """Classify multiple texts."""
        return [self.classify(text) for text in texts]
    
    def analyze_coverage(self, texts: List[str]) -> Dict:
        """
        Analyze topic coverage across a corpus.
        
        Returns stats about how many articles match each topic,
        and how many articles have no matches.
        """
        results = self.classify_batch(texts)
        
        topic_counts = Counter()
        articles_per_topic_count = Counter()  # How many articles have N topics
        no_topic_articles = []
        
        for i, result in enumerate(results):
            num_topics = len(result.topics)
            articles_per_topic_count[num_topics] += 1
            
            if num_topics == 0:
                no_topic_articles.append(i)
            
            for topic in result.topics:
                topic_counts[topic] += 1
        
        return {
            "total_articles": len(texts),
            "topic_counts": dict(topic_counts),
            "articles_by_num_topics": dict(articles_per_topic_count),
            "no_topic_count": len(no_topic_articles),
            "no_topic_indices": no_topic_articles[:20],  # First 20 for inspection
        }


def classify_text(text: str) -> List[str]:
    """Convenience function: return just the topic list."""
    classifier = TopicClassifier()
    return classifier.classify(text).topics


def extract_text_from_html(html_path: str) -> str:
    """Extract text content from an HTML file."""
    from html.parser import HTMLParser
    from pathlib import Path
    
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text_parts = []
            self.in_script = False
            self.in_style = False
        
        def handle_starttag(self, tag, attrs):
            if tag == 'script':
                self.in_script = True
            elif tag == 'style':
                self.in_style = True
        
        def handle_endtag(self, tag):
            if tag == 'script':
                self.in_script = False
            elif tag == 'style':
                self.in_style = False
        
        def handle_data(self, data):
            if not self.in_script and not self.in_style:
                text = data.strip()
                if text:
                    self.text_parts.append(text)
    
    html_content = Path(html_path).read_text(encoding='utf-8', errors='ignore')
    parser = TextExtractor()
    parser.feed(html_content)
    return ' '.join(parser.text_parts)


def test_on_corpus(corpus_dir: str, sample_size: int = 100):
    """
    Test classifier on a sample of HTML files from a corpus.
    
    Args:
        corpus_dir: Path to directory containing HTML files
        sample_size: Number of files to sample
    """
    from pathlib import Path
    import random
    
    corpus_path = Path(corpus_dir)
    html_files = list(corpus_path.glob("**/*.html"))
    
    if not html_files:
        print(f"No HTML files found in {corpus_dir}")
        return
    
    print(f"Found {len(html_files)} HTML files")
    
    # Sample
    sample_files = random.sample(html_files, min(sample_size, len(html_files)))
    
    classifier = TopicClassifier()
    texts = []
    filenames = []
    
    for f in sample_files:
        try:
            text = extract_text_from_html(str(f))
            if len(text) > 100:  # Skip very short files
                texts.append(text)
                filenames.append(f.name)
        except Exception as e:
            print(f"Error reading {f}: {e}")
    
    print(f"Successfully extracted {len(texts)} articles")
    
    # Analyze coverage
    coverage = classifier.analyze_coverage(texts)
    
    print(f"\n=== Coverage Analysis ===")
    print(f"Total articles: {coverage['total_articles']}")
    print(f"\nTopic counts:")
    for topic, count in sorted(coverage['topic_counts'].items(), key=lambda x: -x[1]):
        pct = 100 * count / coverage['total_articles']
        print(f"  {topic}: {count} ({pct:.1f}%)")
    
    print(f"\nArticles by number of topics:")
    for num_topics, count in sorted(coverage['articles_by_num_topics'].items()):
        print(f"  {num_topics} topics: {count} articles")
    
    print(f"\nArticles with NO topics: {coverage['no_topic_count']}")
    
    # Show some no-topic examples
    if coverage['no_topic_indices']:
        print(f"\nSample no-topic articles:")
        for idx in coverage['no_topic_indices'][:5]:
            print(f"  - {filenames[idx]}")
            # Show first 200 chars
            preview = texts[idx][:200].replace('\n', ' ')
            print(f"    Preview: {preview}...")
    
    return coverage, texts, filenames


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test on corpus directory
        corpus_dir = sys.argv[1]
        sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        test_on_corpus(corpus_dir, sample_size)
    else:
        # Demo with sample text
        sample = """
        NASA's Perseverance rover has discovered organic molecules on Mars. 
        The discovery was announced on January 15, 2024, at a press conference 
        held at the Jet Propulsion Laboratory. The rover, which landed in 
        Jezero Crater in February 2021, used its SHERLOC instrument to analyze 
        rock samples. Scientists say the molecules could indicate ancient 
        microbial life, though more research is needed. The mission cost 
        approximately $2.7 billion and is part of NASA's broader Mars 
        exploration program. The samples will eventually be returned to Earth 
        by a future mission planned for the 2030s.
        """
        
        classifier = TopicClassifier()
        result = classifier.classify(sample)
        
        print("Sample classification:")
        print(f"  Topics: {result.topics}")
        print(f"  Scores: {result.scores}")
        print()
        print("Matched keywords by topic:")
        for topic, matches in result.matched_keywords.items():
            if matches:
                print(f"  {topic}: {matches[:5]}")  # Show first 5
        
        print("\n" + "="*50)
        print("To test on your corpus:")
        print("  python topic_classifier.py /path/to/universetoday 100")
