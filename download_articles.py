#!/usr/bin/env python3
"""
Universe Today Article Downloader
Downloads all articles from universetoday.com
"""

import requests
import time
import os
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path
import re


class UniverseTodayDownloader:
    def __init__(self, output_dir="articles", user_agent=None, contact_email=None, project_url=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.base_url = "https://universetoday.com"
        self.session = requests.Session()

        # Set descriptive User-Agent to identify the bot and its purpose
        if user_agent is None:
            user_agent = 'UniverseTodayArchiver/1.0'
            if contact_email:
                user_agent += f' ({contact_email})'
            # Default to the project repository
            if project_url is None:
                project_url = 'https://github.com/stevenchalem/universe'
            user_agent += f' +{project_url}'

        self.session.headers.update({
            'User-Agent': user_agent,
            'From': contact_email if contact_email else '',  # RFC 7231 recommends From header for bots
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        self.delay = 2  # seconds between requests (be respectful)
        self.progress_file = self.output_dir / "download_progress.json"
        self.downloaded_urls = self.load_progress()

    def check_robots_txt(self):
        """Check and display robots.txt for informational purposes"""
        try:
            robots_url = f"{self.base_url}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            if response.status_code == 200:
                print("\n" + "="*50)
                print("robots.txt content:")
                print("="*50)
                print(response.text[:1000])  # First 1000 chars
                if len(response.text) > 1000:
                    print("...(truncated)")
                print("="*50)
                print("Please review robots.txt to ensure compliance.")
                print("="*50 + "\n")
        except Exception as e:
            print(f"Note: Could not fetch robots.txt: {e}")

    def load_progress(self):
        """Load previously downloaded URLs to resume if interrupted"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r') as f:
                return set(json.load(f))
        return set()

    def save_progress(self):
        """Save download progress"""
        with open(self.progress_file, 'w') as f:
            json.dump(list(self.downloaded_urls), f)

    def get_sitemap_urls(self):
        """Fetch all article URLs from sitemap"""
        print("Fetching sitemap...")
        sitemap_url = f"{self.base_url}/sitemap.xml"

        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Handle namespaces
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

            urls = []
            for url in root.findall('.//ns:url/ns:loc', namespaces):
                urls.append(url.text)

            print(f"Found {len(urls)} URLs in sitemap")
            return urls

        except Exception as e:
            print(f"Error fetching sitemap: {e}")
            print("Will try pagination method instead...")
            return None

    def get_article_urls_from_pagination(self, max_pages=None):
        """Get article URLs by crawling through paginated listing"""
        print("Fetching article URLs via pagination...")
        urls = []
        page = 1

        while True:
            if max_pages and page > max_pages:
                break

            page_url = f"{self.base_url}/page/{page}/" if page > 1 else self.base_url

            try:
                print(f"Fetching page {page}...")
                response = self.session.get(page_url, timeout=30)
                response.raise_for_status()

                # Simple regex to find article URLs
                # Universe Today articles typically follow pattern: /YYYY/MM/article-title/
                article_pattern = r'https://universetoday\.com/\d+/\d+/[^"\'<>]+'
                found_urls = re.findall(article_pattern, response.text)

                if not found_urls:
                    print(f"No more articles found on page {page}")
                    break

                # Remove duplicates and add to list
                unique_urls = list(set(found_urls))
                urls.extend(unique_urls)
                print(f"Found {len(unique_urls)} articles on page {page}")

                time.sleep(self.delay)
                page += 1

            except Exception as e:
                print(f"Error on page {page}: {e}")
                break

        # Remove duplicates from all pages
        urls = list(set(urls))
        print(f"Total unique articles found: {len(urls)}")
        return urls

    def sanitize_filename(self, url):
        """Create a safe filename from URL"""
        # Extract path and create a readable filename
        path = urlparse(url).path.strip('/')
        # Replace slashes with underscores
        filename = path.replace('/', '_')
        # Remove any other problematic characters
        filename = re.sub(r'[<>:"|?*]', '', filename)
        return filename + '.html'

    def download_article(self, url):
        """Download a single article"""
        if url in self.downloaded_urls:
            return True

        try:
            print(f"Downloading: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Create filename
            filename = self.sanitize_filename(url)
            filepath = self.output_dir / filename

            # Save HTML content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)

            # Also save metadata
            metadata = {
                'url': url,
                'download_date': datetime.now().isoformat(),
                'status_code': response.status_code
            }

            metadata_file = self.output_dir / (filename + '.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

            self.downloaded_urls.add(url)
            return True

        except Exception as e:
            print(f"Error downloading {url}: {e}")
            return False

    def download_all(self, use_sitemap=True, max_pages=None):
        """Download all articles"""
        print("Starting Universe Today article download...")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"User-Agent: {self.session.headers.get('User-Agent')}")

        # Check robots.txt
        self.check_robots_txt()

        # Get article URLs
        if use_sitemap:
            urls = self.get_sitemap_urls()
            if urls is None:
                urls = self.get_article_urls_from_pagination(max_pages)
        else:
            urls = self.get_article_urls_from_pagination(max_pages)

        if not urls:
            print("No URLs found to download!")
            return

        # Filter out already downloaded
        remaining = [u for u in urls if u not in self.downloaded_urls]
        print(f"\nTotal articles: {len(urls)}")
        print(f"Already downloaded: {len(self.downloaded_urls)}")
        print(f"Remaining: {len(remaining)}")

        # Download each article
        successful = 0
        failed = 0

        for i, url in enumerate(remaining, 1):
            print(f"\n[{i}/{len(remaining)}] ", end='')

            if self.download_article(url):
                successful += 1
            else:
                failed += 1

            # Save progress periodically
            if i % 10 == 0:
                self.save_progress()
                print(f"Progress saved. Success: {successful}, Failed: {failed}")

            # Be respectful - delay between requests
            time.sleep(self.delay)

        # Final save
        self.save_progress()

        print("\n" + "="*50)
        print("Download complete!")
        print(f"Successfully downloaded: {successful}")
        print(f"Failed: {failed}")
        print(f"Total articles: {len(self.downloaded_urls)}")
        print(f"Output directory: {self.output_dir.absolute()}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Download articles from Universe Today')
    parser.add_argument('--output', '-o', default='articles',
                       help='Output directory (default: articles)')
    parser.add_argument('--no-sitemap', action='store_true',
                       help='Use pagination instead of sitemap')
    parser.add_argument('--max-pages', type=int,
                       help='Maximum number of pages to crawl (pagination mode only)')
    parser.add_argument('--delay', type=float, default=2.0,
                       help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--test', action='store_true',
                       help='Test mode: only download first 10 articles')
    parser.add_argument('--email', '-e',
                       help='Your contact email (will be included in User-Agent and From header)')
    parser.add_argument('--project-url', '-p',
                       help='URL for your project/repository (included in User-Agent)')
    parser.add_argument('--user-agent', '-u',
                       help='Custom User-Agent string (overrides default)')

    args = parser.parse_args()

    downloader = UniverseTodayDownloader(
        output_dir=args.output,
        user_agent=args.user_agent,
        contact_email=args.email,
        project_url=args.project_url
    )
    downloader.delay = args.delay

    if args.test:
        print("TEST MODE: Will only download first 10 articles")
        # Get URLs and limit to 10
        urls = downloader.get_sitemap_urls() if not args.no_sitemap else downloader.get_article_urls_from_pagination(max_pages=2)
        if urls:
            test_urls = urls[:10]
            print(f"Testing with {len(test_urls)} articles...")
            for url in test_urls:
                downloader.download_article(url)
                time.sleep(args.delay)
            downloader.save_progress()
    else:
        downloader.download_all(
            use_sitemap=not args.no_sitemap,
            max_pages=args.max_pages
        )


if __name__ == '__main__':
    main()
