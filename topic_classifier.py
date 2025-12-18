#!/usr/bin/env python3
"""
Topic classifier for KG population pipeline.
Given an article, determines which gist topics are relevant.
"""

from typing import List, Dict, Optional, Tuple
import json
import re
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup

# Import available topics from gist_schema
try:
    from gist_schema import available_topics
except ImportError:
    # Fallback if gist_schema not available
    def available_topics():
        return ["organizations", "events", "time", "geo", "agreements",
                "quantities", "content", "collections", "categories",
                "artifacts", "intentions"]


@dataclass
class TopicClassification:
    """Result of topic classification."""
    topics: List[str]
    confidence: Dict[str, float]  # topic -> confidence score
    method: str  # "llm" or "keyword"
    article_id: Optional[str] = None


class KeywordTopicClassifier:
    """
    Fast keyword-based topic classifier.
    Good for initial filtering or when LLM unavailable.
    """

    # Keywords that signal each topic's presence
    TOPIC_KEYWORDS = {
        "organizations": [
            r"\b(NASA|ESA|SpaceX|Boeing|Lockheed|agency|organization|company|"
            r"corporation|government|institution|team|mission control|"
            r"consortium|collaboration|partnership)\b"
        ],
        "events": [
            r"\b(launch|landed|mission|discovery|collision|impact|eclipse|"
            r"transit|event|occurred|happened|detected|observed|exploded|"
            r"crashed|docked|deployed|experiment|test)\b"
        ],
        "time": [
            r"\b(\d{4}|january|february|march|april|may|june|july|august|"
            r"september|october|november|december|monday|tuesday|wednesday|"
            r"thursday|friday|saturday|sunday|yesterday|today|tomorrow|"
            r"years? ago|in \d+ years?|century|decade|millennium|"
            r"billion years|million years)\b"
        ],
        "geo": [
            r"\b(Earth|Mars|Venus|Jupiter|Saturn|Uranus|Neptune|Mercury|Pluto|"
            r"Moon|location|latitude|longitude|crater|mountain|valley|plain|"
            r"region|area|zone|site|landing site|hemisphere|pole|equator)\b"
        ],
        "quantities": [
            r"\b(\d+[\.,]?\d*\s*(km|meter|mile|kg|ton|gram|lightyear|AU|"
            r"parsec|degree|kelvin|celsius|mph|kph|m/s|percent|%|"
            r"kilometers|meters|miles|kilograms|grams|light-years))\b"
        ],
        "content": [
            r"\b(image|photo|video|data|signal|message|communication|"
            r"transmission|paper|study|research|report|publication|"
            r"article|document|recording)\b"
        ],
        "artifacts": [
            r"\b(spacecraft|satellite|rover|lander|probe|telescope|"
            r"instrument|camera|sensor|detector|antenna|rocket|vehicle|"
            r"equipment|device|tool|module)\b"
        ],
        "categories": [
            r"\b(asteroid|comet|planet|star|galaxy|nebula|exoplanet|"
            r"type|class|category|kind|species|genus)\b"
        ],
        "collections": [
            r"\b(catalog|database|survey|collection|archive|set of|"
            r"series of|group of|array|network|constellation)\b"
        ],
        "agreements": [
            r"\b(agreement|contract|treaty|accord|partnership|collaboration|"
            r"memorandum|commitment|obligation)\b"
        ],
        "intentions": [
            r"\b(plan|intend|goal|objective|purpose|aim|target|requirement|"
            r"specification|design|intended)\b"
        ],
        "people": [
            r"\b(?:Dr\.|Prof\.|Professor)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+(?:said|told|explained|noted|added|stated)",
            r"\baccording to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"\b(?:led|directed|headed)\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"\b(?:researcher|scientist|astronomer|physicist|astronaut)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
        ]
    }

    def __init__(self, min_confidence: float = 0.1):
        """
        Args:
            min_confidence: Minimum confidence threshold to include a topic
        """
        self.min_confidence = min_confidence
        # Compile regex patterns
        self.patterns = {}
        for topic, patterns in self.TOPIC_KEYWORDS.items():
            self.patterns[topic] = re.compile(
                "|".join(patterns),
                re.IGNORECASE
            )

    def classify(self, text: str, article_id: Optional[str] = None) -> TopicClassification:
        """
        Classify text using keyword matching.

        Args:
            text: Article text (can include HTML)
            article_id: Optional identifier for tracking

        Returns:
            TopicClassification with matched topics
        """
        # Clean text
        text = self._clean_text(text)

        # Count keyword matches per topic
        matches = {}
        for topic, pattern in self.patterns.items():
            found = pattern.findall(text)
            matches[topic] = len(found)

        # Calculate confidence scores (normalized by text length)
        text_len = len(text.split())
        max_matches = max(matches.values()) if matches else 1

        confidence = {}
        for topic, count in matches.items():
            if count > 0:
                # Normalize by both text length and max matches
                score = (count / text_len) * 100  # per-100-words
                score = min(score, 1.0)  # cap at 1.0
                confidence[topic] = score

        # Filter by threshold and sort by confidence
        topics = [
            topic for topic, score in confidence.items()
            if score >= self.min_confidence
        ]
        topics.sort(key=lambda t: confidence[t], reverse=True)

        return TopicClassification(
            topics=topics,
            confidence=confidence,
            method="keyword",
            article_id=article_id
        )

    def _clean_text(self, text: str) -> str:
        """Extract clean text from HTML if needed."""
        if text.strip().startswith("<"):
            soup = BeautifulSoup(text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            text = soup.get_text()

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class LLMTopicClassifier:
    """
    LLM-based topic classifier using Claude or other models.
    More accurate but slower than keyword classifier.
    """

    def __init__(self,
                 model: str = "claude-3-haiku-20240307",
                 api_key: Optional[str] = None,
                 min_confidence: float = 0.5):
        """
        Args:
            model: Model name (Claude, OpenAI, etc.)
            api_key: API key (will try ENV if not provided)
            min_confidence: Minimum confidence to include topic
        """
        self.model = model
        self.min_confidence = min_confidence
        self.api_key = api_key

        # Try to import anthropic
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.available = True
        except ImportError:
            print("Warning: anthropic package not installed. Install with: pip install anthropic")
            self.available = False

    def classify(self, text: str, article_id: Optional[str] = None) -> TopicClassification:
        """
        Classify text using LLM.

        Args:
            text: Article text
            article_id: Optional identifier

        Returns:
            TopicClassification
        """
        if not self.available:
            raise RuntimeError("LLM classifier not available - install anthropic package")

        # Clean and truncate text if needed
        text = self._prepare_text(text)

        # Build prompt
        prompt = self._build_prompt(text)

        # Call LLM
        message = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse response
        response_text = message.content[0].text
        return self._parse_response(response_text, article_id)

    def _prepare_text(self, text: str, max_words: int = 400) -> str:
        """Clean and truncate text for LLM."""
        if text.strip().startswith("<"):
            soup = BeautifulSoup(text, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            # Get title and main content
            title = soup.find("h1")
            title_text = title.get_text() if title else ""

            # Get article body
            article = soup.find("article")
            if article:
                body_text = article.get_text()
            else:
                body_text = soup.get_text()

            text = f"{title_text}\n\n{body_text}"

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Truncate to max_words
        words = text.split()
        if len(words) > max_words:
            text = " ".join(words[:max_words]) + "..."

        return text

    def _build_prompt(self, text: str) -> str:
        """Build classification prompt."""
        topics = available_topics()
        topic_list = ", ".join(topics)

        return f"""Classify this article by identifying which of these topics are relevant:
{topic_list}

For each relevant topic, provide a confidence score from 0.0 to 1.0.

Topics:
- organizations: Companies, agencies, teams, governments
- events: Launches, discoveries, missions, occurrences
- time: Dates, durations, temporal references
- geo: Locations, places, regions (planets, moons, etc.)
- quantities: Measurements, numbers with units
- content: Images, data, papers, communications
- artifacts: Spacecraft, instruments, equipment
- categories: Classifications, types (asteroid types, star classes)
- collections: Catalogs, databases, sets
- agreements: Contracts, partnerships, collaborations
- intentions: Plans, goals, requirements, specifications

Return ONLY a JSON object with this format:
{{
  "topics": ["topic1", "topic2"],
  "confidence": {{"topic1": 0.9, "topic2": 0.7}}
}}

Article:
{text}"""

    def _parse_response(self, response: str, article_id: Optional[str]) -> TopicClassification:
        """Parse LLM JSON response."""
        # Extract JSON from response (might be wrapped in markdown)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if not json_match:
            raise ValueError(f"No JSON found in LLM response: {response}")

        data = json.loads(json_match.group())

        # Filter by confidence threshold
        topics = [
            t for t in data.get("topics", [])
            if data.get("confidence", {}).get(t, 0) >= self.min_confidence
        ]

        return TopicClassification(
            topics=topics,
            confidence=data.get("confidence", {}),
            method="llm",
            article_id=article_id
        )


class HybridTopicClassifier:
    """
    Two-stage classifier: fast keyword filter, then LLM refinement.
    Balances speed and accuracy.
    """

    def __init__(self,
                 keyword_threshold: float = 0.05,
                 llm_threshold: float = 0.5,
                 model: str = "claude-3-haiku-20240307",
                 api_key: Optional[str] = None):
        """
        Args:
            keyword_threshold: Threshold for keyword stage
            llm_threshold: Threshold for LLM stage
            model: LLM model name
            api_key: API key for LLM
        """
        self.keyword_classifier = KeywordTopicClassifier(min_confidence=keyword_threshold)
        self.llm_classifier = LLMTopicClassifier(
            model=model,
            api_key=api_key,
            min_confidence=llm_threshold
        )

    def classify(self, text: str, article_id: Optional[str] = None) -> TopicClassification:
        """
        Classify using keyword filter, then LLM refinement.

        Args:
            text: Article text
            article_id: Optional identifier

        Returns:
            TopicClassification from LLM (if available) or keywords
        """
        # Fast keyword filter
        keyword_result = self.keyword_classifier.classify(text, article_id)

        if not keyword_result.topics:
            # No topics found, skip LLM
            return keyword_result

        # Refine with LLM if available
        try:
            llm_result = self.llm_classifier.classify(text, article_id)
            return llm_result
        except Exception as e:
            print(f"LLM classification failed, falling back to keywords: {e}")
            return keyword_result


def classify_article_file(
    file_path: Path,
    classifier: Optional[any] = None
) -> TopicClassification:
    """
    Convenience function to classify an article HTML file.

    Args:
        file_path: Path to article HTML
        classifier: Classifier instance (creates KeywordTopicClassifier if None)

    Returns:
        TopicClassification
    """
    if classifier is None:
        classifier = KeywordTopicClassifier()

    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    article_id = file_path.stem
    return classifier.classify(html, article_id=article_id)


def main():
    """Demo classification on sample articles."""
    import sys
    from pathlib import Path

    # Get article directory
    articles_dir = Path("articles")
    if not articles_dir.exists():
        print("No articles directory found")
        return

    # Get first few articles
    html_files = list(articles_dir.glob("*.html"))[:20]

    if not html_files:
        print("No HTML files found in articles/")
        return

    print("=== Keyword-based Topic Classification ===\n")

    classifier = KeywordTopicClassifier(min_confidence=0.05)

    for article_file in html_files:
        result = classify_article_file(article_file, classifier)

        print(f"Article: {article_file.name}")
        print(f"Topics: {', '.join(result.topics)}")
        print(f"Confidence: {json.dumps(result.confidence, indent=2)}")
        print()

    # Try LLM classifier if available
    print("\n=== LLM-based Classification (if available) ===\n")
    try:
        llm_classifier = LLMTopicClassifier(min_confidence=0.5)
        if llm_classifier.available:
            result = classify_article_file(html_files[0], llm_classifier)
            print(f"Article: {html_files[0].name}")
            print(f"Topics: {', '.join(result.topics)}")
            print(f"Confidence: {json.dumps(result.confidence, indent=2)}")
        else:
            print("LLM classifier not available - install anthropic package")
    except Exception as e:
        print(f"LLM classification error: {e}")


if __name__ == "__main__":
    main()
